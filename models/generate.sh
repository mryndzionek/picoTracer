#!/bin/sh

command -v gsl >/dev/null 2>&1
if  [ $? -ne 0 ]; then
    echo "$0: error: could not find gsl.  gsl is required to run $0." 1>&2
    exit 1
fi

if [ "$#" -ne 1 ]; then
    echo "Please provide XML model file as first argument"
    exit 1
fi

export PATH=../codecs:$PATH
gsl -q -script:trace_c $1
gsl -q -script:trace_tests $1
gsl -q -script:trace_python $1
exit $?
