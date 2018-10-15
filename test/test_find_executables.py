import mock
import pytest

import pydot_ng as pydot


def touch(path):
    f = open(path, "w")
    f.close()


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


@pytest.mark.parametrize("quoted", (True, False), ids=("quoted", "unqoted"))
@pytest.mark.parametrize(
    "windows,conda,extension",
    (
        (True, True, "bat"),
        (True, False, "exe"),
        (False, False, "unix"),
        (False, True, "unix"),
    ),
)
@pytest.mark.parametrize(
    "program", ("dot", "twopi", "neato", "circo", "fdp", "sfdp")
)
@mock.patch.object(pydot, "is_anacoda")
@mock.patch.object(pydot, "is_windows")
def test_f_e(
    mock_win, mock_conda, tmpdir, windows, conda, extension, program, quoted
):
    path = tmpdir.mkdir("PYDOT is_da best!")

    mock_win.return_value = windows
    mock_conda.return_value = conda

    unix_path = str(path.join(program))
    touch(unix_path)

    exe_path = str(path.join(program + ".exe"))
    touch(exe_path)

    bat_path = str(path.join(program + ".bat"))
    touch(bat_path)

    if quoted:
        path = '"{}"'.format(path)
        unix_path = '"{}"'.format(unix_path)
        bat_path = '"{}"'.format(bat_path)
        exe_path = '"{}"'.format(exe_path)

    progs = pydot.__find_executables(str(path))

    if extension == "bat":
        assert progs[program] == bat_path
    elif extension == "exe":
        assert progs[program] == exe_path
    elif extension == "unix":
        assert progs[program] == unix_path
    else:
        raise Exception("Unknown extension {}".format(extension))
