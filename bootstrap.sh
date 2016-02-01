#!/bin/sh

if [ -e gen/ ];then
    rm -R gen
fi
mkdir -p gen/src
mkdir -p gen/include
mkdir -p gen/python
mkdir -p gen/tests

