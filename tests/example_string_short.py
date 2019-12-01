from pipedata.types import RawNode,TrackedFile, InputTrackedFile, frame_init
import os

symin, symout, index= frame_init()
print ("[indexFile]",_indexFile)

_f1 = InputTrackedFile('tests-number.txt',name='numberFile')
_f2 = InputTrackedFile('tests-letter.txt',name='letterFile')
# _f3 = InputTrackedFile('tests-dummy.txt',name='dummyFile')
print (_symbolicRootNode.input_kw)

@RawNode.from_func({
    "OUT":TrackedFile("tests-out5.txt",),
})
def out5(  self, (numberFile, letterFile), 
    ):
    '''
    some doc
    '''
    print (type(numberFile()),type(numberFile))
    print (getattr(numberFile(),"values",lambda:())())

    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with open(  self['OUT'].path,'w') as f:
        f.write( 5 * (number+letter)+'\n')

    return


@RawNode.from_func({
    "OUT":TrackedFile("tests-out10.txt"),
})
def out10(  self, (numberFile, letterFile), ):
    '''
    some doc
    '''
    '''
    '''
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with open(self['OUT']().path,'w') as f:
        f.write( 10 * (number+letter)+'\n')
    return


@RawNode.from_func({
    "OUT":TrackedFile("test-combined_short.txt"),
})
def make_combined_short( self, (out5, out15), ):
    lines = []
    [ lines.extend(list(
        open(x()['OUT'].path,'r'))) for x in [out5, out15, ]]
    with open(self['OUT']().path,'w') as f:
        map(f.write,lines)
    return 1

@RawNode.from_func({
    "OUT":TrackedFile("tests-out15.txt"),
})
def out15(  self, (numberFile, letterFile), ):
    '''
    some doc
    '''
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with open(self['OUT']().path,'w') as f:
        f.write( 15 * (number+letter)+'\n')
    return


@RawNode.from_func({
    'OUT':TrackedFile('tests-combined.txt')
})
def make_combined( self, (out5, out10, out15,), ):
    lines = []
    [ lines.extend(list(
        open(x()['OUT'].path,'r'))) for x in [out5, out10, out15, ]]    
    with open(self['OUT']().path,'w') as f:
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