from pipecutter.deps import (
    print_tree,
    build_graph,
    _TASK_COMPLETE_COLOR,
    _TASK_PENDING_COLOR,
)

from tests import MockTask, CompleteDownstreamTask


def test_print_tree():
    print_tree(MockTask())


def test_build_graph():
    import graphviz as gz

    graph = build_graph(CompleteDownstreamTask())

    assert isinstance(graph, gz.Digraph)
    assert len(graph.body) == 3
    for match_str in (
        "MockTask",
        "CompleteDownstreamTask",
        _TASK_COMPLETE_COLOR,
        _TASK_PENDING_COLOR,
    ):
        assert any(match_str in b for b in graph.body)
