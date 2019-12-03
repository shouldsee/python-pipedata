from pipeline_tracker import Node,TrackedFile, InputTrackedFile
import os
_node = Node
INPUT_FILE = InputTrackedFile('test_R1_.fastq')
INPUT_GENOME = InputTrackedFile('test.fa')

# _output_kw = Node.from_func
@Node.from_func({
    "BAM":TrackedFile( "test.fastq.bam"  )
})
def make_bam(  self, INPUT_FILE ):
    '''
    some doc
    '''
#     if INPUT_FILE().changed():
    if self.upstream_changed():
        print("RUNNING:%s"%self)
        lines = list( INPUT_FILE().open('r') )
        with self.output_kw['BAM'].open("w") as f:
            f.write(str(lines))
    else:
        print("SKIPPING:%s"%self)
        pass
    return


@Node.from_func({
})
def make_csv( self, make_bam=make_bam, ):
    make_bam()
#     print make_bam()['BAM']
    return 1


if __name__ == '__main__':
    os.chdir("tests/")
    make_bam()
    make_csv()
#     print("[middle]",middle())