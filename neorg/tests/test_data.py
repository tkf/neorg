from neorg.data import DictTable, GridDict

from itertools import product
from nose.tools import raises, assert_raises, eq_
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



class CheckGridDict(CheckData):

    @staticmethod
    def gene_grid_dict(key_val):
        gd = GridDict(len(key_val[0][0]))
        for (key, val) in key_val:
            gd.append(key, val)
        return gd


class TestGridDictGetItem(CheckGridDict):

    data = [
        ([((0, 0), '00'),
          ((0, 1), '01'),
          ((0, 1), '01 (2)'),
          ((0, 1), '01 (3)'),
          ((0, 2), '02'),
          ((1, 1), '11')],
         ),
        ([((0, 0, 0), '000'),
          ((1, 1, 1), '111'),
          ((2, 2, 2), '222')],
         ),
        ([((i, j * 0.1), None)
          for i in range(3) for j in range(4)
          if i != j],
         ),
        ([((i, j * 0.1, str(k)), None)
          for i in range(3) for j in range(4) for k in range(5)
          if not (i == j == k and i == j + 1 == k + 2)],
         ),
        ]

    def check(self, key_val):
        gd = self.gene_grid_dict(key_val)
        for key in product(*gd.axes):
            vals = [v for (k, v) in key_val if k == key]
            assert gd[key] == vals
            expr  = 'gd[key] == gd[%s]' % ']['.join(map(repr, key))
            assert eval(expr, {'gd': gd, 'key': key})


class TestGridDictAppendRaiseError(TestGridDictGetItem):

    def check(self, key_val):
        gd = self.gene_grid_dict(key_val)
        num_test = 0
        for num in range(gd.num - 1):
            for key in product(*gd.axes):
                assert_raises(KeyError, gd.append, key[:num], None)
                num_test += 1
        for key in product(*gd.axes):
            gd.append(key, None)
            num_test += 1
        for key in product(*gd.axes):
            bigkey = key + (key[0],)
            assert_raises(KeyError, gd.append, bigkey, None)
            num_test += 1
        num_grid = 1
        for axis in gd.axes:
            num_grid *= len(axis)
        eq_(num_test, num_grid * (gd.num + 1))


class TestDictTableGeneDictCheckNum(CheckData):

    dict_a = gene_dict('a', 'b', 'c.d', 'c.e')
    dict_b_replaces = {'val_b': 'replaced_b',
                       'val_c_e': 'replaced_c_e'}
    dict_b = gene_dict('a', 'b', 'c.d', 'c.e', **dict_b_replaces)

    data = [
        ({'name_a': dict_a, 'name_b': dict_b},
         ['b', ('c', 'e')],
         4,
         2,
         ),
        ({'name_a': dict_a, 'name_b': dict_b},
         ['b', ('c', 'e'), 'unknown'],
         4,
         2,
         ),
        ({'name_a': dict_a, 'name_a_dash': dict_a, 'name_b': dict_b},
         ['b', ('c', 'e')],
         4,  # volume does not change. no change in the parameter space.
         3,  # stored names increase for the point (val_b, val_c_e)
         ),
        ]

    @staticmethod
    def volume(axes):
        num = 1
        for a in axes:
            num *= len(a)
        return num

    @staticmethod
    def stored(gd):
        num = 0
        for key in product(*gd.axes):
            num += len(gd[key])
        return num

    def check(self, dict_data, key_list, volume, stored):
        dt = DictTable(dict_data)
        gd = dt.grid_dict(key_list)
        assert self.volume(gd.axes) == volume
        assert self.stored(gd) == stored
