class NEOrgVersion(object):
    """
    Versioning algorithm for NEOrg

    >>> V = NEOrgVersion
    >>> (V('0.0.1')
    ...  < V('0.0.2.dev0')
    ...  < V('0.0.2.dev1')
    ...  < V('0.0.2.dev41')
    ...  < V('0.0.2.dev182')
    ...  < V('0.0.3'))
    True
    >>> V('0.1')
    Traceback (most recent call last):
      ...
    ValueError: '0.1' is not valid NEOrg version string
    >>> V('a.b')
    Traceback (most recent call last):
      ...
    ValueError: first three parts must be integers. given version string: 'a.b'

    Some ideas and implementations from here:
    `PEP 386 -- Changing the version comparison module in Distutils
    <http://www.python.org/dev/peps/pep-0386/>`_

    """

    def __init__(self, verstr):
        self._verstr = verstr

        verstrtuple = verstr.split('.')
        try:
            numparts = map(int, verstrtuple[:3])
        except ValueError:
            raise ValueError(
                "first three parts must be integers. "
                "given version string: '{0}'".format(verstr))
        if len(verstrtuple) == 3:
            self.parts = tuple(numparts) + ('f', )
        elif len(verstrtuple) == 4 and verstrtuple[3].startswith('dev'):
            dev = verstrtuple[3][len('dev'):]
            self.parts = tuple(numparts) + ('dev', int(dev))
        else:
            raise ValueError(
                "'{0}' is not valid NEOrg version string".format(verstr))

    def __str__(self):
        return self._verstr

    def __repr__(self):
        return "{0}('{1}')".format(self.__class__.__name__, self)

    def _cannot_compare(self, other):
        raise ValueError(
            "cannot compare {0} and {1}".fromat(type(self).__name__,
                                                type(other).__name__))

    def __eq__(self, other):
        if not isinstance(other, NEOrgVersion):
            self._cannot_compare(other)
        return self.parts == other.parts

    def __lt__(self, other):
        if not isinstance(other, NEOrgVersion):
            self._cannot_compare(other)
        return self.parts < other.parts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not (self.__lt__(other) or self.__eq__(other))

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)


def current_version():
    from neorg import __version__
    return NEOrgVersion(__version__)
