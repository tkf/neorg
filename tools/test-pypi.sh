#!/bin/bash

# this script is used for testing the neorg package uploaded to pypi

PYPITESTDIR='.pypitest'

# clear PYTHONPATH
PYTHONPATH=
export PYTHONPATH

NOSE_DOCTEST_TESTS=t
NOSE_WITH_DOCTEST=t
export NOSE_DOCTEST_TESTS
export NOSE_WITH_DOCTEST


if [ -d doc/ -a -d neorg/ ]
then
    mkdir -pv $PYPITESTDIR
    cd $PYPITESTDIR
    mkdir -pv log

    PYPITESTLOG=log/pypitest-`date +%F-%H%M%S`.log
    echo "log: $PYPITESTDIR/$PYPITESTLOG"

    echo "PWD: $PWD" >> $PYPITESTLOG
    if [ -d "env" ]
    then
	echo "virtualenv exists" >> $PYPITESTLOG
    else
	echo "create virtualenv" >> $PYPITESTLOG
	virtualenv --no-site-packages env >> $PYPITESTLOG 2>&1
    fi
    source env/bin/activate >> $PYPITESTLOG 2>&1
    pip install nose mock texttable >> $PYPITESTLOG 2>&1
    pip install -U neorg >> $PYPITESTLOG 2>&1
    if python -c \
	"import neorg; assert neorg.__file__.startswith('$PWD/env/')"
    then
	{
	    echo "NEOrg is ready!"
	    echo "Using:"
	    echo "    neorg: `which neorg`"
	    echo "    nosetests: `which nosetests`"
	} >> $PYPITESTLOG 2>&1
    else
	echo "NEOrg is imported from other directory."
	echo "Cannot test correctly in this setting."
	exit 1
    fi
    nosetests neorg >> $PYPITESTLOG 2>&1
    NEORG_FASTTEST=t nosetests neorg.tests.test_web >> $PYPITESTLOG 2>&1
else
    echo "Execute $0 at root of the working directory."
    echo 'You should see `doc/` and `nerog/` directories.'
    exit 1
fi

# see also:
# http://jenkins-ci.org/content/python-love-story-virtualenv-and-hudson
