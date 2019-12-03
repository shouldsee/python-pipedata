
## pipedata

A lightweight package that version controls pipeline and data.

### Installation

```bash
pip2 install pipedata@https://github.com/shouldsee/python-pipedata/tarball/master --user
pip2 install https://github.com/shouldsee/python-pipedata/tarball/master --user
```

### Test

```bash
bash test.sh
```
### To-Do

1. Add meta functionality

1. IndexNode() best be pruned when flushing. 
  - clean_index() should prune dangling records.
  - migrate_code() should copy source to a new location and drop all outputs
  - migrate_both() should copy both source and data to a new location
  - migrate() should consider whether the upstream branch should be migrated

1. _Fixed with `pipedata.base.IndexNode()`_ ~~separate pipe_run.py from test_all.py, ideally each pipeline should be constructed upon module import ~~

1. ~~rename pipedata.py to types.py~~

1. (Tip) careful with inspect.getsource

1. _skip for now_  ~~python3 for now_ Python3 OrderedDict is wicked...~~
```
  File "/usr/lib/python3.6/pickle.py", line 496, in save
    rv = reduce(self.proto)
TypeError: can't pickle odict_keys objects
```

1. _See TrackedDict_ ~~Add a variableNode~~

1. (Complicated) figure out whether to use absolute or relative path 
  - pipedata.base.TrackedFile() use realpath() for caching

1. (Delayed) Go fully atomic by backing up old file 
