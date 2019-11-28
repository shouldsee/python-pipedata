from pipedata import AutoNode as Node
from pipedata import TrackedFile, InputTrackedFile, index_file_flush
import os
_node = Node
numberFile = InputTrackedFile('number.txt')
letterFile = InputTrackedFile('letter.txt')
import time
# _output_kw = Node.from_func
@Node.from_func({
    "OUT":TrackedFile("out5.txt"),
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
    "OUT":TrackedFile("out10.txt"),
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
    "OUT":TrackedFile("out15.txt"),
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
    'OUT':TrackedFile('combined.txt')
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
    
    TrackedFile.VERBOSE=0
    print('START'+20*"-")
    os.chdir("tests/")
    res = make_combined()
    index_file_flush("./test.index")
    print(res['OUT'].open('r').read())
#     open(''))
    print('END'+20*"-")
    import dill
    dill.dumps(make_combined)
    
#     make_bam()
#     make_csv()
#     print("[middle]",middle())