from pipeline_tracker import RawNode as Node
from pipeline_tracker import TrackedFile, InputTrackedFile, index_file_flush
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
    if self.changed_upstream() or self.force:
        print("RUNNING:%s"%self)
        number = numberFile().open('r').read().strip()
        letter = letterFile().open('r').read().strip()
#         lines = list( INPUT_FILE().open('r') )
        with self.output_kw['OUT'].open("w") as f:
            f.write( 5 * (number+letter)+'\n')
    else:
        print("SKIPPING:%s"%self)
        pass
    return


@Node.from_func({
    "OUT":TrackedFile("out10.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out10(  self, numberFile, letterFile ):
    '''
    some doc
    '''
    if self.changed_upstream() or self.force:
        print("RUNNING:%s"%self)
        number = numberFile().open('r').read().strip()
        letter = letterFile().open('r').read().strip()
#         lines = list( INPUT_FILE().open('r') )
        with self['OUT'].open("w") as f:
            f.write( 10 * (number+letter)+'\n')
        self['OUT'].index_update()   
    else:
        print("SKIPPING:%s"%self)
        pass
    return

@Node.from_func({
    "OUT":TrackedFile("out15.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out15(  self, numberFile, letterFile ):
    '''
    some doc
    '''
    if self.changed_upstream() or self.force:
        print("RUNNING:%s"%self)
        number = numberFile().open('r').read().strip()
        letter = letterFile().open('r').read().strip()
#         lines = list( INPUT_FILE().open('r') )
        with self.output_kw['OUT'].open("w") as f:
            f.write( 15 * (number+letter)+'\n')
        self['OUT'].index_update()   
#         index_file_update(self['OUT'])
    else:
        print("SKIPPING:%s"%self)
        pass
    return

@Node.from_func({
    'OUT':TrackedFile('combined.txt')
})
def make_combined( self, out5, out10, out15, ):
    if self.changed_upstream() or self.force:
        lines = []
        [ lines.extend(list(x()['OUT'].open('r'))) for x in [out5,
                                                             out10,out15
                                                            ]]
        print out5()['OUT'].path
        print lines
        with self['OUT'].open('w') as f:
            map(f.write,lines)
        self['OUT'].index_update()   
    else:
        print("SKIPPING:%s"%self)
#     make_bam()
    return 1


if __name__ == '__main__':
    
    os.chdir("tests/")
    make_combined()
    index_file_flush("./test.index")