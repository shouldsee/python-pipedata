from pipedata import index_file_flush

def pipe_run(self):
#     pipe.TrackedFile.VERBOSE=0
    # !rm -f {pipe.index.path}
    # print pipe.index.
    print('START' + 20*"-")
    # nodes = [self._symbolicOutputNode.input_kw]
    self._symbolicOutputNode()
    # for x in  self._symbolicOutputNode.input_kw
    # print( self._symbolicOutputNode().input_kw['make_combined']['OUT'].open('r').read())
    index_file_flush(fname=self._indexFile,)
    print('END' + 20*"-")