#!/bin/sh

# Generate document for coffee-script files in build/docco/docs/

cd $(dirname $0)/../
mkdir -p build/docco
cd build/docco
pwd
docco ../../neorg/static/*.coffee
