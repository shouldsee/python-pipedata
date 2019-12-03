import os,sys
sys.path.insert(0, os.getcwd())
from pipedata.base import RawNode,TrackedFile, InputTrackedFile,  IndexNode
from pipedata.types import TrackedDict,RemoteNode,MasterNode
import os
index = IndexNode()
# assert 0
from pymisca.shell import shellexec as _shell

_d = TrackedDict(index,'meta', 
    dict(DATA_ACC="ABC123"))

_ = '''
if remote out5 is triggered, its index will be put into queue but not flushed.
There are two choices here: 
  1. leave the upstream in a non-synced state, by caching a unsync flag into the influenced nodes, 
    - for TrackedFile, this has to override the default
    - The default backbone in a level_stream is RawNode. It should take all its output with it,
    if the funcion opens a TrackedFile and modified it, it does not differ if the TrackedFile
    index_update() itself or whether its triggered by the main_node(), because the timestamp 
    is the same.
    - however, for TrackedDict() the result of as_record() depends on whether the main_node has
    been executed. One solution would be dump the dictionary into a TrackedFile. Because the 
    data comes from the execution of the main_node(), it would not be possible to predict it
    unless the main_node is executed, 

  2. The easier option would be to update the upstream to be in sync.
  - in order to test for this, alter out5.txt, run the downstream script and check the status of combined.txt
  
'''
RemoteNode(index,remote_path='../stage1/pipe.py',remote_name='out5')

@MasterNode.from_func(index,)
def main(s,(out5,),(meta,)):
    # out5.initialised
    # print (out5.remote_entity,)
    print ("[result]",out5(),out5())
    ########################
    #### Needs fixing
    # meta.data['result'] = s
    s = (open(out5()['OUT'].realpath(),"r").read())
    return s
    # out5.index_update()


if __name__ == '__main__':
    # from pipedata.base import index_file_flush

    TrackedFile.VERBOSE=0
    print('START' + 20*"-")
    # symout()
    # print(symout())
    # .input_kw['make_combined']['OUT'].open('r').read())
    index.index_file_flush()
    print('END' + 20*"-")
    
    import dill
    import json
    print json.dumps(dill.load(open(index.path)),indent=4)
    # dill.dumps(symout)