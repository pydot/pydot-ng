# coding=iso-8859-1

from __future__ import division
from __future__ import print_function

import os
import sys
import warnings
from textwrap import dedent

import mock
import pytest

import pydot_ng as pydot


PY3 = not sys.version_info < (3, 0, 0)

if PY3:
    NULL_SEP = b""
    xrange = range
else:
    NULL_SEP = ""
    bytes = str


DOT_BINARY_PATH = pydot.find_graphviz()["dot"]
TEST_DIR = os.path.dirname(__file__)
REGRESSION_TESTS_DIR = os.path.join(TEST_DIR, "graphs")
MY_REGRESSION_TESTS_DIR = os.path.join(TEST_DIR, "my_tests")


@pytest.fixture
def digraph():
    return pydot.Graph("testgraph", graph_type="digraph")


@pytest.mark.parametrize("graph_type", ("graph", "digraph"))
def test_keep_graph_type(graph_type):
    graph = pydot.Dot(graph_name="Test", graph_type=graph_type)
    assert graph.get_type() == graph_type
    assert graph.graph_type == graph_type


def test_node_style():
    node = pydot.Node("mynode")
    assert node.get_style() is None

    node.add_style("abc")
    assert node.get_style() == "abc"

    node.add_style("def")
    assert node.get_style() == "abc,def"

    node.add_style("ghi")
    assert node.get_style() == "abc,def,ghi"


def test_create_simple_graph_with_node():
    graph = pydot.Dot(graph_type="digraph")

    node = pydot.Node("legend")
    node.set("shape", "box")
    node.set("label", "mine")

    graph.add_node(node)

    assert graph.to_string() == dedent(
        """\
        digraph G {
        legend [label=mine, shape=box];
        }
        """
    )


def test_attribute_with_implicit_value():
    dot = dedent(
        """
    digraph {
    na -> b[label="hi", decorate];
    }
    """
    )
    graph = pydot.graph_from_dot_data(dot)
    edge = graph.get_edges()[0]
    attrs = edge.get_attributes()
    assert attrs == {"decorate": None, "label": '"hi"'}


def test_subgraphs():
    graph = pydot.Graph()
    subgraph = pydot.Subgraph("foo")

    assert graph.get_subgraphs() == []
    assert graph.get_subgraph_list() == []

    graph.add_subgraph(subgraph)

    assert len(graph.get_subgraphs()) == 1
    assert len(graph.get_subgraph_list()) == 1

    assert graph.get_subgraphs()[0].get_name() == subgraph.get_name()
    assert graph.get_subgraph_list()[0].get_name() == subgraph.get_name()


def test_graph_is_picklabe():
    import pickle

    graph = pydot.Graph()
    subgraph = pydot.Subgraph("foo")
    graph.add_subgraph(subgraph)
    graph.add_edge(pydot.Edge("A", "B"))
    graph.add_edge(pydot.Edge("A", "C"))
    graph.add_edge(pydot.Edge(("D", "E")))
    graph.add_node(pydot.Node("node!"))

    assert isinstance(pickle.dumps(graph), bytes)


def test_unicode_ids():
    node1 = '"aánñoöüé€"'
    node2 = '"îôø®çßΩ"'

    graph = pydot.Dot()
    graph.set_charset("latin1")
    graph.add_node(pydot.Node(node1))
    graph.add_node(pydot.Node(node2))
    graph.add_edge(pydot.Edge(node1, node2))

    assert graph.get_node(node1)[0].get_name() == node1
    assert graph.get_node(node2)[0].get_name() == node2

    assert graph.get_edges()[0].get_source() == node1
    assert graph.get_edges()[0].get_destination() == node2

    graph2 = pydot.graph_from_dot_data(graph.to_string())

    assert graph2.get_node(node1)[0].get_name() == node1
    assert graph2.get_node(node2)[0].get_name() == node2

    assert graph2.get_edges()[0].get_source() == node1
    assert graph2.get_edges()[0].get_destination() == node2


def test_parse_multiple_graphs():
    graph_data = dedent(
        """\
        graph A { a->b };
        graph B {c->d}
        """
    )
    graphs = pydot.graph_from_dot_data(graph_data)
    assert len(graphs) == 2
    assert sorted(g.get_name() for g in graphs) == sorted(["A", "B"])


def test_numeric_node_id(digraph):
    digraph.add_node(pydot.Node(1))
    assert digraph.get_nodes()[0].get_name() == "1"


def test_quoted_node_id(digraph):
    digraph.add_node(pydot.Node('"node"'))
    assert digraph.get_nodes()[0].get_name() == '"node"'


def test_quoted_node_id_to_string_no_attributes(digraph):
    digraph.add_node(pydot.Node('"node"'))
    assert digraph.get_nodes()[0].to_string() == '"node";'


def test_keyword_node_id(digraph):
    digraph.add_node(pydot.Node("node"))
    assert digraph.get_nodes()[0].get_name() == "node"


def test_keyword_node_id_to_string_no_attributes(digraph):
    digraph.add_node(pydot.Node("node"))
    assert digraph.get_nodes()[0].to_string() == ""


def test_keyword_node_id_to_string_with_attributes(digraph):
    digraph.add_node(pydot.Node("node", shape="box"))
    assert digraph.get_nodes()[0].to_string() == "node [shape=box];"


def test_names_of_a_thousand_nodes(digraph):
    names = set(["node_%05d" % i for i in xrange(10 ** 4)])

    for name in names:
        digraph.add_node(pydot.Node(name, label=name))

    assert set([n.get_name() for n in digraph.get_nodes()]) == names


def test_executable_not_found_exception():
    graph = pydot.Dot("graphname", graph_type="digraph")

    paths = {"dot": "invalid_executable_path"}
    graph.set_graphviz_executables(paths)

    with pytest.raises(pydot.InvocationException):
        graph.create()


@pytest.mark.parametrize("node", (1, "a", None))
def test_graph_add_node_argument_type(digraph, node):
    with pytest.raises(TypeError) as exc_info:
        digraph.add_node(node)

    assert "add_node() received a non node class object" in str(exc_info.value)


@pytest.mark.parametrize("edge", (1, "a", None))
def test_graph_add_edge_argument_type(digraph, edge):
    with pytest.raises(TypeError) as exc_info:
        digraph.add_edge(edge)

    assert "add_edge() received a non edge class object" in str(exc_info.value)


@pytest.mark.parametrize("subgraph", (1, "a", None))
def test_graph_add_subgraph_argument_type(digraph, subgraph):
    with pytest.raises(TypeError) as exc_info:
        digraph.add_subgraph(subgraph)
    assert "add_subgraph() received a non subgraph class object" in str(
        exc_info.value
    )


def test_quoting():
    import string

    g = pydot.Dot()
    g.add_node(pydot.Node("test", label=string.printable))
    data = g.create(format="jpe")
    assert len(data) > 0


@pytest.mark.parametrize(
    "input, expected",
    (
        ("A:", '"A:"'),
        (":B", '":B"'),
        ("A:B", "A:B"),
        ("1A", '"1A"'),
        ("A", "A"),
        ("11", "11"),
        ("_xyz", "_xyz"),
        (".11", '".11"'),
        ("-.09", '"-.09"'),
        ("1.8", '"1.8"'),
        # ('', '""'),
        ('"1abc"', '"1abc"'),
        ("@", '"@"'),
        ("ÿ", '"ÿ"'),
        (
            "$GUID__/ffb73e1c-7495-40b3-9618-9e5462fc89c7",
            '"$GUID__/ffb73e1c-7495-40b3-9618-9e5462fc89c7"',
        ),
    ),
)
def test_quote_if_necessary(input, expected):
    assert pydot.quote_if_necessary(input) == expected


@pytest.mark.xfail(
    (3, 7) > sys.version_info >= (3, 6),
    reason="python 3.6 on Travis is failing this and no way to debug it now",
)
def test_dotparser_import_warning():
    with mock.patch.dict(sys.modules, {"pydot_ng._dotparser": None}):
        with pytest.warns(
            UserWarning,
            match="Couldn't import _dotparser, loading"
            " of dot files will not be possible.",
        ):
            del sys.modules["pydot_ng"]
            warnings.simplefilter("always")
            import pydot_ng  # noqa: F401


def test_find_executables_fake_path():
    assert pydot.__find_executables("/fake/path/") is None


def test_find_executables_real_path_no_programs(tmpdir):
    assert pydot.__find_executables(str(tmpdir)) is None


def test_find_executables_path_needs_strip(tmpdir):
    path = tmpdir.mkdir("subdir")
    prog_path = str(path.join("dot"))

    path_with_spaces = "    {}     ".format(path)

    with open(prog_path, "w"):
        progs = pydot.__find_executables(path_with_spaces)
        assert progs["dot"] == prog_path
        assert sorted(
            ("dot", "twopi", "neato", "circo", "fdp", "sfdp")
        ) == sorted(progs)


def test_find_executables_unix_and_exe_exists(tmpdir):
    path = str(tmpdir)
    prog_unix_path = str(tmpdir.join("dot"))
    prog_exe_path = str(tmpdir.join("dot.exe"))

    with open(prog_unix_path, "w"):
        with open(prog_exe_path, "w"):
            progs = pydot.__find_executables(path)
            assert progs["dot"] == prog_unix_path
            assert progs["dot"] != prog_exe_path


@pytest.mark.parametrize("quoted", (True, False), ids=("quoted", "unqoted"))
@pytest.mark.parametrize("extension", ("", ".exe"))
@pytest.mark.parametrize(
    "program", ("dot", "twopi", "neato", "circo", "fdp", "sfdp")
)
def test_find_executables(tmpdir, program, extension, quoted):
    path = tmpdir.mkdir("PYDOT is_da best!")
    prog_path = str(path.join(program + extension))

    with open(prog_path, "w"):
        if quoted:
            path = "\"{}\"".format(path)
            prog_path = "\"{}\"".format(prog_path)

        progs = pydot.__find_executables(str(path))
        assert progs[program] == prog_path
        assert sorted(
            ("dot", "twopi", "neato", "circo", "fdp", "sfdp")
        ) == sorted(progs)
