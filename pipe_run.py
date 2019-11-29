from pipedata import index_file_flush

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
#     pipe.TrackedFile.VERBOSE=0
    # !rm -f {pipe.index.path}
    # print pipe.index.
    print('START' + 20*"-")
    # nodes = [self._symbolicOutputNode.input_kw]
    # self._symbolicOutputNode()
    [x() for x in self._symbolicRootNode.input_kw.values()]
    print os.path.realpath( self._indexFile )
    # for x in  self._symbolicOutputNode.input_kw
    # print( self._symbolicOutputNode().input_kw['make_combined']['OUT'].open('r').read())
    index_file_flush(fname=self._indexFile,)
    print('END' + 20*"-")