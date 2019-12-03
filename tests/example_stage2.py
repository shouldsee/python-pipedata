import os,sys
from pipedata.types import IndexNode
from pipedata.types import SelfSlaveFile, MasterNode
from pipedata.types import RemoteNode

index = IndexNode()
RemoteNode(index, remote_path='../stage1/pipe.py',remote_name='out5')

@MasterNode.from_func(index,)
def main(s,(out5,),
    ):
    print ("[result]",out5(),out5())
    s = (open(out5()['OUT'].realpath(),"r").read())
    return s

if __name__ == '__main__':
    index.main()
    # print('START' + 20*"-")
    # [x() for x in index.node_dict.values()]
    # index.index_file_flush()
    # print('END' + 20*"-")
