from itertools import product

from neorg.verutils import NEOrgVersion


def test_version_str():
    for verstr in ['0.0.1', '0.0.2.dev0', '1.2.3.dev45']:
        assert str(NEOrgVersion(verstr)) == verstr


def test_version_parse():
    for (i, j, k, l) in product(*([range(10)] * 4)):
        if l == 0:
            NEOrgVersion('{0}.{1}.{2}'.format(i, j, k))
        NEOrgVersion('{0}.{1}.{2}.dev{3}'.format(i, j, k, l))


def test_version_compare():
    for (i, j, k, l) in product(*([range(1, 10)] * 4)):
        if l == 0:
            assert (
                NEOrgVersion('{0}.{1}.{2}'.format(i, j, k)) ==
                NEOrgVersion('{0}.{1}.{2}'.format(i, j, k)))
            for ijk0 in [(i - 1, j, k),
                         (i, j - 1, k),
                         (i, j, k - 1)]:
                assert (
                    NEOrgVersion('{0}.{1}.{2}'.format(i, j, k)) >
                    NEOrgVersion('{0}.{1}.{2}'.format(*ijk0)))
        assert (
            NEOrgVersion('{0}.{1}.{2}'.format(i, j, k)) >
            NEOrgVersion('{0}.{1}.{2}.dev{3}'.format(i, j, k, l)))
        assert (
            NEOrgVersion('{0}.{1}.{2}.dev{3}'.format(i, j, k, l)) ==
            NEOrgVersion('{0}.{1}.{2}.dev{3}'.format(i, j, k, l)))
        for ijkl0 in [(i - 1, j, k, l),
                      (i, j - 1, k, l),
                      (i, j, k - 1, l),
                      (i, j, k, l - 1)]:
            assert (
                NEOrgVersion('{0}.{1}.{2}.dev{3}'.format(i, j, k, l)) >
                NEOrgVersion('{0}.{1}.{2}.dev{3}'.format(*ijkl0)))
