# from pipedata.base import index_file_flush

import imp
import os
# def _load_source(name, fn,):
#     suff, mode, TYPE = describ = ('.py','U',1)
#     if name is None:
#         name = fn.rsplit('/',1)[-1][:-len(suff)]
#     with open(fn,mode) as f:
#         mod = imp.load_module( name, f,fn, describ)
#     return mod

def pipe_run(self):
    print('START' + 20*"-")
    [ x() for x in self.node_dict.values()]
    self.index_file_flush()
    print('END' + 20*"-")