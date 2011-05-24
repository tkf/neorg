from neorg.data import DictTable

from nose.tools import raises
from neorg.tests.utils import CheckData


def gene_dict(*keys, **replace):
    """Generate dictionary for testing"""
    def gene_val(keytuple):
        value = 'val_%s' % '_'.join(keytuple)
        value = replace.get(value, value)
        return value
    parse_key = DictTable().parse_key
    keys = [parse_key(k) for k in keys]
    vals = [gene_val(keytuple) for keytuple in keys]
    return DictTable()._gene_dict(zip(keys, vals))


class TestGeneDict(CheckData):

    data = [
        (('a', 'b', 'c.d', 'c.e'),
         {},
         {'a': 'val_a', 'b': 'val_b', 'c': {'d': 'val_c_d',
                                            'e': 'val_c_e'}}),
        (('a', 'b', 'c.d', 'c.e'),
         {'val_c_e': 'replaced'},
         {'a': 'val_a', 'b': 'val_b', 'c': {'d': 'val_c_d',
                                            'e': 'replaced'}}),
        ]

    def check(self, args, kwds, desired):
        generated = gene_dict(*args, **kwds)
        assert generated == desired


class TestGeneDictFail(TestGeneDict):

    data = [
        (('a', 'b', 'c.d', 'c.e'),
         {},
         {'a': 'val_a', 'b': 'val_b', 'c': {'d': 'val_c_d',
                                            'e': 'WRONG'}}),
        (('a', 'b', 'c.d', 'c.e'),
         {'val_c_e': 'replaced'},
         {'a': 'val_a', 'b': 'val_b', 'c': {'d': 'val_c_d',
                                            'e': 'WRONG'}}),
        ]

    check = raises(AssertionError)(TestGeneDict.check)


def assert_eq(**kwds):
    keyval = list(kwds.iteritems())
    (k0, v0) = keyval.pop()
    for (k, v) in keyval:
        err_msg = '\n'.join([
            "%s != %s" % (k, k0),
            "%s:" % k0,
            repr(v0),
            "%s:" % k,
            repr(v),
            ])
        assert v0 == v, err_msg


class TestDictTableFilterByFnmatch(CheckData):

    dict_a = gene_dict('a', 'b', 'c.d', 'c.e')
    dict_b_replaces = {'val_b': 'replaced_b',
                       'val_c_e': 'replaced_c_e'}
    dict_b = gene_dict('a', 'b', 'c.d', 'c.e', **dict_b_replaces)
    dict_n = gene_dict('1', '2', '3.4', '5.6')

    data = [
        ({'name_a': dict_a},
         (['a', 'b'],),
         {},
         {'name_a': gene_dict('a', 'b')},
         ),
        ({'name_a': dict_a},
         (['*'],),
         {},
         {'name_a': dict_a},
         ),
        ({'name_a': dict_a},
         (['c.*'],),
         {},
         {'name_a': gene_dict('c.d', 'c.e')},
         ),
        ({'name_a': dict_a, 'name_b': dict_b},
         (['c.*'],),
         {},
         {'name_a': gene_dict('c.d', 'c.e'),
          'name_b': gene_dict('c.d', 'c.e', **dict_b_replaces)},
         ),
        ({'name_a': dict_a, 'name_b': dict_b, 'name_n': dict_n},
         (['*'],),
         {},
         {'name_a': dict_a, 'name_b': dict_b, 'name_n': dict_n},
         ),
        ]

    def test_data(self):
        assert self.dict_a != self.dict_b
        assert self.dict_a != self.dict_n
        assert self.dict_n != self.dict_b

    def check(self, dict_data, args, kwds, dict_data_desired):
        dt = DictTable(dict_data)
        dt_desired = DictTable(dict_data_desired)
        dt_filtered = dt.filter_by_fnmatch(*args, **kwds)
        assert_eq(dt_desired=dt_desired, dt_filtered=dt_filtered)
