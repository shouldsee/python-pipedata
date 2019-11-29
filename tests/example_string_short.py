import pipedata; 
from pipedata import AutoNode as Node
from pipedata import RawNode
from pipedata import TrackedFile, InputTrackedFile, OutputTrackedFile, frame_init
import os

import time

symin, symout, index= frame_init()
print "[indexFile]",_indexFile
numberFile = InputTrackedFile('tests-number.txt')
letterFile = InputTrackedFile('tests-letter.txt')

# _output_kw = Node.from_func
@Node.from_func({
    "OUT":TrackedFile("tests-out5.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out5(  self, numberFile, letterFile ):
    '''
    some doc
    '''
    number = numberFile().open('r').read().strip()
    letter = letterFile().open('r').read().strip()
    with self.output_kw['OUT'].open("w") as f:
        f.write( 5 * (number+letter)+'\n')
    return


@Node.from_func({
    "OUT":TrackedFile("tests-out10.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out10(  self, numberFile, letterFile ):
    '''
    some doc
    '''
    number = numberFile().open('r').read().strip()
    letter = letterFile().open('r').read().strip()
    with self.output_kw['OUT'].open("w") as f:
        f.write( 10 * (number+letter)+'\n')
    return

@Node.from_func({
    "OUT":TrackedFile("tests-out15.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out15(  self, numberFile, letterFile ):
    '''
    some doc
    '''
    number = numberFile().open('r').read().strip()
    letter = letterFile().open('r').read().strip()
    with self.output_kw['OUT'].open("w") as f:
        f.write( 15 * (number+letter)+'\n')
    return


@Node.from_func({
    'OUT':TrackedFile('tests-combined.txt')
})
def make_combined( self, out5, out10, out15, ):
    lines = []
    [ lines.extend(list(x()['OUT'].open('r'))) for x in [out5,
                                                         out10,out15
                                                        ]]
    with self['OUT'].open('w') as f:
        map(f.write,lines)
    return 1


if __name__ == '__main__':
    from pipedata import index_file_flush

    TrackedFile.VERBOSE=0
    print('START' + 20*"-")
    symout()
    print(symout().input_kw['make_combined']['OUT'].open('r').read())
    index_file_flush()
    print('END' + 20*"-")
    
    import dill
    dill.dumps(symout)
#     dill.dumps(make_combined)
#     print symout
    
#     make_bam()
#     make_csv()
#     print("[middle]",middle())