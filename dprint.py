#!/usr/bin/env python2
#/work/repos/pipedata/test_build/stage1/pipe.py.index
import dill
import sys,json
sys.stdout.write(json.dumps(dill.load(open(sys.argv[1],"r")),default=repr,indent=4))
