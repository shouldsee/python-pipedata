import os,sys
sys.path.insert(0, os.getcwd())
from pipedata.base import RawNode,TrackedFile, InputTrackedFile,  IndexNode
from pipedata.types import TrackedDict,RemoteNode
import os
index = IndexNode()
# assert 0
from pymisca.shell import shellexec as _shell

_d = TrackedDict(index,'meta', 
    dict(DATA_ACC="ABC123"))

RemoteNode(index,remote_path='test_build/pipe.py',remote_name='out5')

@RawNode.from_func(index)
def main(s,(out5,)):
    # out5.initialised
    # print (out5.remote_entity,)
    print ("[result]",out5(),out5())
    print(open(out5()['OUT'].realpath(),"r").read())
    # out5.index_update()

main()

if 0:
    _ = '''
    Connect to upstream and relay calling
    Should declare dependency across scripts
    '''
    GenomeIndexFile = RemoteTrackedFile(path = "/tmp/genome/ath", acc="bowtie2_index")

    @RawNode.from_func()
    def print_params(s,(paramDict,GenomeIndexFile)):
        for k,v in paramDict.data:
            print(k,v)

    @RawNode.from_func()
    def bowtie2_align():
        _shell(["bowtie2",
            "-1",FASTQ_F1,
            "-2",FASTQ_F2])
        return 

    @RawNode.from_func()
    def macs_peak_calling():
        _shell
        return 

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