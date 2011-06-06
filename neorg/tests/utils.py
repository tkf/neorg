import sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from mock import Mock
import neorg.data


class MockWeb(object):
    """
    Mock for `neorg.web`
    """

    def __init__(self,
                 datadirpath='MOCK_DATADIRPATH',
                 datadirurl='MOCK_DATADIRURL',
                 list_descendants=['./SubPage', './Sub/SubPage']):
        app = self.app = Mock()
        app.config = {}
        app.config['DATADIRPATH'] = datadirpath
        app.config['DATADIRURL'] = datadirurl

        self.list_descendants = Mock(return_value=list_descendants)


class MockDictTable(neorg.data.DictTable):
    """
    Mock for `neorg.data.DictTable`
    """

    _file_tree = {
        'file_1.json': {'a': 1},
        'file_2.yaml': {'a': 2},
        'file_3.pickle': {'a': 3},
        }

    @classmethod
    def new_mock(cls, file_tree):
        """
        Generate new mock with the new fake file tree
        """
        class new_class(cls):
            _file_tree = file_tree.copy()
        return new_class

    @classmethod
    def load_any(cls, path, ftype=None):
        if path in cls._file_tree:
            return cls._file_tree[path]
        else:
            raise IOError(
                "No such file in the fake file tree:'%s'" % path)


class CheckData(object):
    data = None  # needs override

    def check(self, *args):
        raise NotImplementedError

    def test(self):
        for args in self.data:
            yield (self.check,) + tuple(args)


def trim(docstring):
    """
    Trim indentation in the docstring way

    Copied from `PEP 257 -- Docstring Conventions
    <http://www.python.org/dev/peps/pep-0257/>`_

    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


class CaptureStdIO(object):

    def __enter__(self):
        import sys
        self._orig_stdin = sys.stdin
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr

        self.stdin = sys.stdin = StringIO()
        self.stdout = sys.stdout = StringIO()
        self.stderr = sys.stderr = StringIO()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdin = self._orig_stdin
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr

    def read_stdout(self):
        self.stdout.seek(0)
        return self.stdout.read()

    def read_stderr(self):
        self.stderr.seek(0)
        return self.stderr.read()


class ChangeNEOrgVersion(object):
    import neorg
    from neorg.verutils import NEOrgVersion

    def __init__(self, verstr):
        self.NEOrgVersion(verstr)  # make sure it is a valid version
        self.verstr = verstr

    def __enter__(self):
        self.true_version = self.neorg.__version__
        self.neorg.__version__ = self.verstr
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.neorg.__version__ = self.true_version
