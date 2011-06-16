#!/bin/sh

# checking long description which is embedded in __init__.py

htmlpath=.long-description.html

if [ -d doc/ -a -d neorg/ ]
then
    (cd neorg && cog.py -r __init__.py) && \
        python setup.py --long-description | rst2html > $htmlpath
    gnome-open $htmlpath
    echo "hg status"
    hg status  # maybe cog.py updated  __init__.py
else
    echo "Execute $0 at root of the working directory."
    echo 'You should see `doc/` and `nerog/` directories.'
    exit 1
fi
