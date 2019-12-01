## pipedata

A lightweight package that version controls pipeline and data.

### Installation

```bash
pip2 install pipedata@https://github.com/shouldsee/python-pipedata/tarball/master --user
pip2 install https://github.com/shouldsee/python-pipedata/tarball/master --user
```

### Test

```bash
python2 test.py
```
### To-Do

1. separate pipe_run.py from test_all.py, ideally each pipeline should be constructed upon module import 

1. rename pipedata.py to types.py

1. careful with inspect.getsource

1. Python3 OrderedDict is wicked...
```
  File "/usr/lib/python3.6/pickle.py", line 496, in save
    rv = reduce(self.proto)
TypeError: can't pickle odict_keys objects
```

1. Add a variableNode

1. figure out whether to use absolute or relative path 
