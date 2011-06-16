#!/bin/sh

python setup.py build
nosetests --with-xunit
touch nosetests.xml --date="$(date)"

NEORG_FASTTEST=True nosetests \
    --with-xunit --xunit-file=nosetests-fast-test.xml \
    neorg/tests/test_web.py
touch nosetests-fast-test.xml --date="$(date)"

# note: `touch` is a workaround for incorrect NFS system time setting
