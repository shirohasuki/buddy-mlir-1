# RUN: %PYTHON %s 2>&1 | FileCheck %s

import torch
import torch._dynamo as dynamo
from torch._inductor.decomposition import decompositions as inductor_decomp
from torch._functorch.aot_autograd import aot_autograd_decompositions

from buddy.compiler.frontend import DynamoCompiler
from buddy.compiler.ops import linalg


def foo(x, y, z):
    return torch.where(x, y, z)


in1 = torch.ones([13, 13], dtype=torch.bool)
in2 = 0  # or in2 is tensor value, i.e. in2 = torch.zeros([13, 13], dtype=torch.float32)
in3 = torch.ones(
    [13, 13], dtype=torch.float32
)  # or in3 is scalar value, i.e. in3 = 1
# Initialize the dynamo compiler.
dynamo_compiler = DynamoCompiler(
    primary_registry=linalg.ops_registry,
    aot_autograd_decomposition=aot_autograd_decompositions,
)

graphs = dynamo_compiler.importer(foo, in1, in2, in3)
assert len(graphs) == 1
graph = graphs[0]
graph.lower_to_top_level_ir()
print(graph._imported_module)

# CHECK: module {
# CHECK-LABEL: func.func @forward
# CHECK: %{{.*}} = arith.constant
# CHECK: %{{.*}} = tensor.empty
# CHECK: %{{.*}} = linalg.generic
# CHECK: return %{{.*}}
# CHECK: }
# CHECK: }
