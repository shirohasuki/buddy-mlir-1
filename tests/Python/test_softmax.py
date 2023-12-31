# RUN: %PYTHON %s 2>&1 | FileCheck %s

import torch
import torch._dynamo as dynamo
from torch._inductor.decomposition import decompositions as inductor_decomp
from torch._functorch.aot_autograd import aot_autograd_decompositions

from buddy.compiler.frontend import DynamoCompiler
from buddy.compiler.ops import linalg


def foo(x):
    return torch.softmax(x, dim=0)


in1 = torch.ones([13, 13], dtype=torch.float32)
# Initialize the dynamo compiler.
dynamo_compiler = DynamoCompiler(
    primary_registry=linalg.ops_registry,
    aot_autograd_decomposition=aot_autograd_decompositions,
)

graphs = dynamo_compiler.importer(foo, in1)
assert len(graphs) == 1
graph = graphs[0]
graph.lower_to_top_level_ir()
print(graph._imported_module)

# CHECK: module {
# CHECK-LABEL: func.func @forward
# CHECK: %{{.*}} = tensor.empty
# CHECK: %{{.*}} = linalg.generic
# CHECK: %{{.*}} = linalg.generic
# CHECK: %{{.*}} = tensor.empty
# CHECK: %{{.*}} = linalg.generic
# CHECK: %{{.*}} = tensor.empty
# CHECK: %{{.*}} = linalg.generic
# CHECK: %{{.*}} = linalg.generic
# CHECK: %{{.*}} = tensor.empty
# CHECK: %{{.*}} = linalg.generic
# CHECK: return %{{.*}}
# CHECK: }
# CHECK: }
