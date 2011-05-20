#!/bin/sh

if [ -d doc/ -a -d neorg/ ]
then
    echo "==> building document" && \
        make -C doc clean html && \
        echo "==> removing old help"  && \
        rm -rf neorg/static/help && \
        echo "==> coping new help" && \
        cp -r doc/build/html neorg/static/help && \
        echo "done!"
else
    echo "Execute $0 at root of the working directory."
    echo 'You should see `doc/` and `nerog/` directories.'
    exit 1
fi
