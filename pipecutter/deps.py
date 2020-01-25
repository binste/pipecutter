import warnings

import luigi
from luigi.task import flatten
from luigi.tools.deps_tree import print_tree as luigi_print_tree

_TASK_COMPLETE_COLOR = "#03C800"
_TASK_PENDING_COLOR = "blue"


def print_tree(task: luigi.Task) -> None:
    print(luigi_print_tree(task))


def build_graph(task: luigi.Task) -> None:
    try:
        import graphviz as gv
    except ImportError as err:
        raise ImportError("You need to install graphviz first") from err

    graph = gv.Digraph(
        strict=True, node_attr={"shape": "rectangle", "fontname": "Helvetica"}
    )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            action="ignore",
            message="Task .* without outputs has no custom complete\\(\\) method",
        )
        graph = _build_graph(graph, task)
    return graph


def _build_graph(graph, task, parent=None):
    is_complete = task.complete()
    color = _TASK_COMPLETE_COLOR if is_complete else _TASK_PENDING_COLOR
    status = "COMPLETE" if is_complete else "PENDING"

    graph.node(
        task.task_id,
        f"<{task.__repr__()}<br/>"
        + f'<font point-size="10" color="{color}">{status}</font>>',
    )
    if parent:
        graph.edge(task.task_id, parent.task_id)

    children = flatten(task.requires())
    for c in children:
        graph = _build_graph(graph, c, task)
    return graph
