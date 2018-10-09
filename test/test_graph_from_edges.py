# -*- coding: utf-8 -*-

import functools
from textwrap import dedent

import pytest

import pydot_ng


@pytest.mark.parametrize(
    "directed, graph_type",
    ((True, "digraph"), (False, "graph")),
    ids=("graph", "digraph"),
)
@pytest.mark.parametrize("edges", (None, [], ()), ids=(None, "list", "tuple"))
def test_empty_list(directed, graph_type, edges):
    graph = pydot_ng.graph_from_edges(edges, directed=directed)

    assert graph.graph_type == graph_type
    assert graph.to_string() == dedent(
        """\
        {graph_type} G {{
        }}
        """.format(
            graph_type=graph_type
        )
    )
    assert not graph.get_edges()


@pytest.mark.parametrize(
    "prefix", ("", "some_prefix_"), ids=("no prefix", "prefix")
)
@pytest.mark.parametrize("src", (1, 2.123, "a", "ą", True))
@pytest.mark.parametrize("dst", (1, 2.123, "a", "ą", True))
def test_edge_types(prefix, src, dst):
    input_edges = [(src, dst)]
    graph = pydot_ng.graph_from_edges(input_edges, node_prefix=prefix)

    edges = graph.get_edges()
    assert len(edges) == 1
    edge = edges[0]

    with_prefix = functools.partial("{0}{1}".format, prefix)

    assert edge.source == pydot_ng.quote_if_necessary(with_prefix(src))
    assert edge.destination == pydot_ng.quote_if_necessary(with_prefix(dst))


@pytest.mark.parametrize(
    "prefix, output",
    (
        (
            "",
            dedent(
                """\
        graph G {
        1 -- 2;
        2 -- "3.14";
        "3.14" -- a;
        a -- "ą";
        "ą" -- True;
        }
        """
            ),
        ),
        (
            "prefix_",
            dedent(
                """\
        graph G {
        prefix_1 -- prefix_2;
        prefix_2 -- "prefix_3.14";
        "prefix_3.14" -- prefix_a;
        prefix_a -- "prefix_ą";
        "prefix_ą" -- prefix_True;
        }
        """
            ),
        ),
    ),
    ids=("no prefix", "prefix"),
)
def test_from_edge_to_string(prefix, output):
    input_edges = [(1, 2), (2, 3.14), (3.14, "a"), ("a", "ą"), ("ą", True)]

    graph = pydot_ng.graph_from_edges(input_edges, node_prefix=prefix)
    assert len(graph.get_edges()) == len(input_edges)
    assert graph.to_string() == output
