import onnx_graphsurgeon as gs
import numpy as np
import onnx
import cupy as cp

import tensorrt as trt
from polygraphy.backend.trt import (
    CreateConfig,
    EngineFromNetwork,
    NetworkFromOnnxPath,
    TrtRunner,
)
from polygraphy.comparator import Comparator
from polygraphy.json import to_json, from_json
import torch

def volume(d):
    return np.prod(d)

class CircPadPlugin(trt.IPluginV2DynamicExt):
    def __init__(self, fc=None):
        trt.IPluginV2DynamicExt.__init__(self)
        self.pads = []
        self.X_shape = []
        self.plugin_namespace = ""

        if fc is not None:
            assert fc[0].name == "pads"
            self.pads = fc[0].data

    def initialize(self):
        return 0

    def get_num_outputs(self):
        return 1

    def get_output_datatype(self, index, input_types):
        return input_types[0]

    def get_output_dimensions(self, output_index, inputs, exprBuilder):

        out_dims = np.array(X.shape)

        output_dims = trt.DimsExprs(inputs[0])

        for i in range(np.size(self.pads) // 2):
            output_dims[len(output_dims) - i - 1] = exprBuilder.operation(
                trt.DimensionOperation.SUM,
                inputs[0][len(output_dims) - i - 1],
                exprBuilder.constant(self.pads[i * 2] + self.pads[i * 2 + 1]),
            )

        return output_dims

    def get_serialization_size(self):
        return len(to_json({"pads": self.pads}))

    def serialize(self):
        return to_json({"pads": self.pads})

    def configure_plugin(self, inp, out):
        X_dims = inp[0].desc.dims
        self.X_shape = np.zeros((len(X_dims),))
        for i in range(len(X_dims)):
            self.X_shape[i] = X_dims[i]

    def supports_format_combination(self, pos, in_out, num_inputs):
        assert num_inputs == 1
        assert pos < len(in_out)

        desc = in_out[pos]
        if desc.format != trt.TensorFormat.LINEAR:
            return False

        # first input should be float16 or float32
        if pos == 0:
            return desc.type == trt.DataType.FLOAT or desc.type == trt.DataType.HALF

        # output should have the same type as the input
        if pos == 1:
            return in_out[0].type == desc.type

        assert False

    def get_workspace_size(self, input_desc, output_desc):
        return 0

    def enqueue(self, input_desc, output_desc, inputs, outputs, workspace, stream):

        inp_dtype = trt.nptype(input_desc[0].type)

        a_mem = cp.cuda.UnownedMemory(
            inputs[0], volume(input_desc[0].dims) * cp.dtype(inp_dtype).itemsize, self
        )
        c_mem = cp.cuda.UnownedMemory(
            outputs[0],
            volume(output_desc[0].dims) * cp.dtype(inp_dtype).itemsize,
            self,
        )

        a_ptr = cp.cuda.MemoryPointer(a_mem, 0)
        c_ptr = cp.cuda.MemoryPointer(c_mem, 0)

        a_d = cp.ndarray(tuple(input_desc[0].dims), dtype=inp_dtype, memptr=a_ptr)
        c_d = cp.ndarray((volume(output_desc[0].dims)), dtype=inp_dtype, memptr=c_ptr)

        a_t = torch.as_tensor(a_d, device='cuda')

        # Use PyTorch functional op - no need to write kernel
        out = torch.nn.functional.pad(a_t, self.pads.tolist(), mode='circular')
        cp.copyto(c_d, cp.reshape(cp.asarray(out), (-1,)))

        return 0

    def destroy(self):
        pass

    def clone(self):
        cloned_plugin = CircPadPlugin.__new__(CircPadPlugin)
        trt.IPluginV2DynamicExt.__init__(cloned_plugin, self)
        cloned_plugin.__dict__.update(self.__dict__)
        return cloned_plugin

    def terminate(self):
        pass

    def get_plugin_namespace(self):
        return self.namespace

    def set_plugin_namespace(self, namespace):
        self.namespace = namespace

    def get_plugin_type(self):
        return "CircPadPlugin"

    def get_plugin_version(self):
        return "1"

    def __getstate__(self):
        return {"pads": self.pads}


class CircPadPluginCreator(trt.IPluginCreator):
    def __init__(self):
        trt.IPluginCreator.__init__(self)
        self.plugin_name = "CircPadPlugin"
        self.namespace = ""
        self.version = "1"
        self.plugin_field_names = trt.PluginFieldCollection(
            [trt.PluginField("pads", np.array([]), trt.PluginFieldType.INT32)]
        )

    def get_plugin_name(self):
        return self.plugin_name

    def get_plugin_version(self):
        return self.version

    def get_field_names(self):
        return self.plugin_field_names

    def create_plugin(self, name, fc):
        return CircPadPlugin(fc)

    def deserialize_plugin(self, name, data):
        deserialized = CircPadPlugin()
        j = dict(from_json(data))
        deserialized.__dict__.update(j)
        return deserialized

    def get_plugin_namespace(self):
        return self.namespace

    def set_plugin_namespace(self, namespace):
        self.namespace = namespace

precision = np.float16

inp_shape = (10, 3, 32, 32)
X = np.random.normal(size=inp_shape).astype(precision)

pads = (1, 1, 1, 1)

# Register plugin creator
plg_registry = trt.get_plugin_registry()
my_plugin_creator = CircPadPluginCreator()
plg_registry.register_creator(my_plugin_creator, "")

# create ONNX model
onnx_path = "test_CircPadPlugin.onnx"
inputA = gs.Variable(name="X", shape=inp_shape, dtype=precision)
Y = gs.Variable(name="Y", dtype=precision)
myPluginNode = gs.Node(
    name="CircPadPlugin",
    op="CircPadPlugin",
    inputs=[inputA],
    outputs=[Y],
    attrs={"pads": pads},
)
graph = gs.Graph(nodes=[myPluginNode], inputs=[inputA], outputs=[Y], opset=16)
onnx.save(gs.export_onnx(graph), onnx_path)

# build engine
build_engine = EngineFromNetwork(
    NetworkFromOnnxPath(onnx_path), CreateConfig(fp16=precision==np.float16)
)

# run
results = Comparator.run(
    [TrtRunner(build_engine, "trt_runner")], warm_up=10, data_loader=[{"X": X}]
)

Y_ref = np.pad(X, [[0, 0], [0, 0], [pads[0], pads[1]], [pads[2], pads[3]]], "wrap")
Y = results["trt_runner"][0]["Y"]

if np.allclose(Y, Y_ref):
    print("Inference result correct!")