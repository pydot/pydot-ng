# coding=iso-8859-1

# TODO(ksambor)
# -test graph generation APIs (from adjacency, etc..)
# -test del_node, del_edge methods
# -test Common.set method

from __future__ import division
from __future__ import print_function

import os
import sys

import pydot_ng as pydot
import unittest2 as unittest


PY3 = not sys.version_info < (3, 0, 0)

if PY3:
    NULL_SEP = b''
    xrange = range
else:
    NULL_SEP = ''
    bytes = str


DOT_BINARY_PATH = pydot.find_graphviz()['dot']
TEST_DIR = os.path.dirname(__file__)
REGRESSION_TESTS_DIR = os.path.join(TEST_DIR, 'graphs')
MY_REGRESSION_TESTS_DIR = os.path.join(TEST_DIR, 'my_tests')


class TestGraphAPI(unittest.TestCase):

    def setUp(self):
        self._reset_graphs()

    def _reset_graphs(self):
        self.graph_directed = pydot.Graph('testgraph', graph_type='digraph')

    def test_keep_graph_type(self):
        g = pydot.Dot(graph_name='Test', graph_type='graph')
        self.assertEqual(g.get_type(), 'graph')
        g = pydot.Dot(graph_name='Test', graph_type='digraph')
        self.assertEqual(g.get_type(), 'digraph')

    def test_add_style(self):
        node = pydot.Node('mynode')
        node.add_style('abc')
        self.assertEqual(node.get_style(), 'abc')
        node.add_style('def')
        self.assertEqual(node.get_style(), 'abc,def')
        node.add_style('ghi')
        self.assertEqual(node.get_style(), 'abc,def,ghi')

    def test_create_simple_graph_with_node(self):
        g = pydot.Dot()
        g.set_type('digraph')
        node = pydot.Node('legend')
        node.set("shape", 'box')
        g.add_node(node)
        node.set('label', 'mine')

        self.assertEqual(g.to_string(),
                         'digraph G {\nlegend [label=mine, shape=box];\n}\n')

    def test_attribute_with_implicit_value(self):
        d = 'digraph {\na -> b[label="hi", decorate];\n}'
        g = pydot.graph_from_dot_data(d)
        attrs = g.get_edges()[0].get_attributes()

        self.assertEqual('decorate' in attrs, True)

    def test_subgraphs(self):
        g = pydot.Graph()
        s = pydot.Subgraph("foo")

        self.assertEqual(g.get_subgraphs(), [])
        self.assertEqual(g.get_subgraph_list(), [])

        g.add_subgraph(s)

        self.assertEqual(g.get_subgraphs()[0].get_name(), s.get_name())
        self.assertEqual(g.get_subgraph_list()[0].get_name(), s.get_name())

    def test_graph_pickling(self):
        import pickle

        g = pydot.Graph()
        s = pydot.Subgraph("foo")
        g.add_subgraph(s)
        g.add_edge(pydot.Edge('A', 'B'))
        g.add_edge(pydot.Edge('A', 'C'))
        g.add_edge(pydot.Edge(('D', 'E')))
        g.add_node(pydot.Node('node!'))

        self.assertEqual(type(pickle.dumps(g)), bytes)

    def test_unicode_ids(self):
        node1 = '"aánñoöüé€"'
        node2 = '"îôø®çßΩ"'

        g = pydot.Dot()
        g.set_charset('latin1')
        g.add_node(pydot.Node(node1))
        g.add_node(pydot.Node(node2))
        g.add_edge(pydot.Edge(node1, node2))

        self.assertEqual(g.get_node(node1)[0].get_name(), node1)
        self.assertEqual(g.get_node(node2)[0].get_name(), node2)

        self.assertEqual(g.get_edges()[0].get_source(), node1)
        self.assertEqual(g.get_edges()[0].get_destination(), node2)

        g2 = pydot.graph_from_dot_data(g.to_string())

        self.assertEqual(g2.get_node(node1)[0].get_name(), node1)
        self.assertEqual(g2.get_node(node2)[0].get_name(), node2)

        self.assertEqual(g2.get_edges()[0].get_source(), node1)
        self.assertEqual(g2.get_edges()[0].get_destination(), node2)

    def test_multiple_graphs(self):
        graph_data = 'graph A { a->b };\ngraph B {c->d}'
        graphs = pydot.graph_from_dot_data(graph_data)
        self.assertEqual(len(graphs), 2)
        self.assertEqual([g.get_name() for g in graphs], ['A', 'B'])

    def test_numeric_node_id(self):
        self._reset_graphs()
        self.graph_directed.add_node(pydot.Node(1))
        self.assertEqual(self.graph_directed.get_nodes()[0].get_name(), '1')

    def test_quoted_node_id(self):
        self._reset_graphs()
        self.graph_directed.add_node(pydot.Node('"node"'))
        self.assertEqual(self.graph_directed.get_nodes()[0].get_name(),
                         '"node"')

    def test_quoted_node_id_to_string_no_attributes(self):
        self._reset_graphs()
        self.graph_directed.add_node(pydot.Node('"node"'))
        self.assertEqual(self.graph_directed.get_nodes()[0].to_string(),
                         '"node";')

    def test_keyword_node_id(self):
        self._reset_graphs()
        self.graph_directed.add_node(pydot.Node('node'))
        self.assertEqual(self.graph_directed.get_nodes()[0].get_name(),
                         'node')

    def test_keyword_node_id_to_string_no_attributes(self):
        self._reset_graphs()
        self.graph_directed.add_node(pydot.Node('node'))
        self.assertEqual(self.graph_directed.get_nodes()[0].to_string(), '')

    def test_keyword_node_id_to_string_with_attributes(self):
        self._reset_graphs()
        self.graph_directed.add_node(pydot.Node('node', shape='box'))
        self.assertEqual(self.graph_directed.get_nodes()[0].to_string(),
                         'node [shape=box];')

    def test_names_of_a_thousand_nodes(self):
        self._reset_graphs()
        names = set(['node_%05d' % i for i in xrange(10 ** 4)])

        for name in names:
            self.graph_directed.add_node(pydot.Node(name, label=name))

        self.assertEqual(set([n.get_name() for n in
                              self.graph_directed.get_nodes()]), names)

    def test_executable_not_found_exception(self):
        paths = {'dot': 'invalid_executable_path'}
        graph = pydot.Dot('graphname', graph_type='digraph')
        graph.set_graphviz_executables(paths)
        self.assertRaises(pydot.InvocationException, graph.create)

    def test_graph_add_node_argument_type(self):
        self._reset_graphs()
        self.assertRaises(TypeError, self.graph_directed.add_node, 1)
        self.assertRaises(TypeError, self.graph_directed.add_node, 'a')

    def test_graph_add_edge_argument_type(self):
        self._reset_graphs()
        self.assertRaises(TypeError, self.graph_directed.add_edge, 1)
        self.assertRaises(TypeError, self.graph_directed.add_edge, 'a')

    def test_graph_add_subgraph_argument_type(self):
        self._reset_graphs()
        self.assertRaises(TypeError, self.graph_directed.add_subgraph, 1)
        self.assertRaises(TypeError, self.graph_directed.add_subgraph, 'a')

    def test_quoting(self):
        import string
        g = pydot.Dot()
        g.add_node(pydot.Node("test", label=string.printable))
        data = g.create(format='jpe')
        self.assertEqual(len(data) > 0, True)


class TestQuoting(unittest.TestCase):

    # TODO(prmtl): this need to be checked with DOT lang
    # sepcification (or how graphviz works) again
    def test_quote_cases(self):
        checks = (
            ('A:', '"A:"'),
            (':B', '":B"'),
            ('A:B', 'A:B'),
            ('1A', '"1A"'),
            ('A', 'A'),
            ('11', '11'),
            ('_xyz', '_xyz'),
            ('.11', '".11"'),
            ('-.09', '"-.09"'),
            ('1.8', '"1.8"'),
            # ('', '""'),
            ('"1abc"', '"1abc"'),
            ('@', '"@"'),
            ('ÿ', '"ÿ"'),
            ('$GUID__/ffb73e1c-7495-40b3-9618-9e5462fc89c7',
             '"$GUID__/ffb73e1c-7495-40b3-9618-9e5462fc89c7"')
        )

        for input, expected in checks:
            self.assertEqual(pydot.quote_if_necessary(input), expected)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraphAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)
