import os,sys
sys.path.insert(0, os.getcwd())
from pipedata.types import RawNode,TrackedFile, InputTrackedFile, frame_init, Pipeline,TrackedDict,_dict, RemoteNode
# sys.path.insert(0, os.getcwd()+"/..")
symin, symout, index= frame_init()
print ("[indexFile]",_indexFile.path)
# assert 0
from pymisca.shell import shellexec as _shell

_d = TrackedDict('meta', 
    dict(DATA_ACC="ABC123"))

RemoteNode(remote_path='test_build/pipe.py',remote_name='out5')

@RawNode.from_func()
def main(s,(out5,)):
    # out5.initialised

    # print (out5.remote_entity,)
    print ("[result]",out5(),out5())
    out5.index_update()


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
    from pipedata.base import index_file_flush

    TrackedFile.VERBOSE=0
    print('START' + 20*"-")
    symout()
    print(symout())
    # .input_kw['make_combined']['OUT'].open('r').read())
    index_file_flush()
    print('END' + 20*"-")
    
    import dill
    dill.dumps(symout)