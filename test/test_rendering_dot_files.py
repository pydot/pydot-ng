from __future__ import division
from __future__ import print_function

import glob
import os
import subprocess
import sys
from hashlib import sha256

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

TESTS_DIRS = (
    ("regressions", REGRESSION_TESTS_DIR),
    ("my_regressions", MY_REGRESSION_TESTS_DIR),
)


def list_dots(path):
    searchpath = os.path.join(path, "*.dot")
    return [f for f in glob.glob(searchpath)]


def pytest_generate_tests(metafunc):
    if metafunc.function != test_render_and_compare_dot_files:
        return

    idlist = []
    argvalues = []
    for name, dir in TESTS_DIRS:
        for filepath in list_dots(dir):
            filename = os.path.basename(filepath)
            idlist.append("{}-{}".format(name, filename))
            argvalues.append((filepath,))
    metafunc.parametrize(
        argnames=["filepath"],
        argvalues=argvalues,
        ids=idlist,
        scope="function",
    )


def _render_with_graphviz(filename):
    p = subprocess.Popen(
        (DOT_BINARY_PATH, "-Tjpe"),
        cwd=os.path.dirname(filename),
        stdin=open(filename, "rt"),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    stdout = p.stdout

    stdout_output = list()
    while True:
        data = stdout.read()
        if not data:
            break
        stdout_output.append(data)
    stdout.close()

    if stdout_output:
        stdout_output = NULL_SEP.join(stdout_output)

    # this returns a status code we should check
    p.wait()

    return sha256(stdout_output).hexdigest()


def _render_with_pydot(filename):
    g = pydot.graph_from_dot_file(filename)
    if not isinstance(g, list):
        g = [g]
    jpe_data = NULL_SEP.join([_g.create(format="jpe") for _g in g])
    return sha256(jpe_data).hexdigest()


def test_render_and_compare_dot_files(filepath):
    parsed_data_hexdigest = _render_with_pydot(filepath)
    original_data_hexdigest = _render_with_graphviz(filepath)

    assert original_data_hexdigest == parsed_data_hexdigest


def test_graph_with_shapefiles():
    shapefile_dir = os.path.join(TEST_DIR, "from-past-to-future")
    dot_file = os.path.join(shapefile_dir, "from-past-to-future.dot")

    pngs = [
        os.path.join(shapefile_dir, fname)
        for fname in os.listdir(shapefile_dir)
        if fname.endswith(".png")
    ]

    with open(dot_file, "rt") as f:
        graph_data = f.read()
    #
    g = pydot.graph_from_dot_data(graph_data)
    g.set_shape_files(pngs)
    jpe_data = g.create(format="jpe")
    hexdigest = sha256(jpe_data).hexdigest()
    hexdigest_original = _render_with_graphviz(dot_file)

    assert hexdigest == hexdigest_original
