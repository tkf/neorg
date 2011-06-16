#!/bin/sh

[ -d neorg/static/ ] && \
    echo "rm -rf neorg/static/help" && \
    rm -rf neorg/static/help && \
    make --directory doc clean && \
    python setup.py build && \
    python setup.py register sdist bdist_egg upload
