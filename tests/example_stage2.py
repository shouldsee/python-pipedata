import os,sys
sys.path.insert(0, os.getcwd())
from pipedata.base import RawNode,TrackedFile, InputTrackedFile,  IndexNode
from pipedata.types import TrackedDict,RemoteNode,MasterNode
import os
index = IndexNode()
# assert 0

# _d = TrackedDict(index,'meta', 
#     dict(DATA_ACC="ABC123"))

RemoteNode(index, remote_path='../stage1/pipe.py',remote_name='out5')

@MasterNode.from_func(index,)
def main(s,(out5,),
    # (meta,)
    ):
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