import os,sys
sys.path.insert(0,os.getcwdu())

from pipedata.base import RawNode,TrackedFile, InputTrackedFile,  IndexNode
from pipedata.types import TrackedDict
from pipedata.types import MasterNode

index = IndexNode()
# symin, symout, index= frame_init()
# print ("[indexFile]",_indexFile)
print ("[indexFile]",index)

# _f1 = InputTrackedFile('tests-number.txt',name='numberFile')
# _f2 = InputTrackedFile('tests-letter.txt',name='letterFile')
_f1 = InputTrackedFile( index, 'tests-number.txt',name='numberFile')
_f2 = InputTrackedFile( index, 'tests-letter.txt',name='letterFile')
# _f3 = InputTrackedFile('tests-dummy.txt',name='dummyFile')
print (index._symbolicRootNode.input_kw)

_p = TrackedDict(index, data={"a":1,"I am in the original script":2} , name='paramDict')

@MasterNode.from_func(index,
    {
    "OUT":TrackedFile(index, "tests-out5.txt",),
})
def out5(  self, (numberFile, letterFile, paramDict), 
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

if 0:

    @RawNode.from_func(index,
        {
        "OUT":TrackedFile(index,"tests-out10.txt"),
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


    @RawNode.from_func(index,
        {
        "OUT":TrackedFile(index,"test-combined_short.txt"),
    })
    def make_combined_short( self, (out5, out15), ):
        lines = []
        [ lines.extend(list(
            open(x()['OUT'].path,'r'))) for x in [out5, out15, ]]
        with open(self['OUT']().path,'w') as f:
            map(f.write,lines)
        return 1

    @RawNode.from_func(index,{
        "OUT":TrackedFile(index,"tests-out15.txt"),
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


    @RawNode.from_func(index,{
        'OUT':TrackedFile(index,'tests-combined.txt')
    })
    def make_combined( self, (out5, out10, out15,), ):
        lines = []
        [ lines.extend(list(
            open(x()['OUT'].path,'r'))) for x in [out5, out10, out15, ]]    
        with open(self['OUT']().path,'w') as f:
             map(f.write,lines)
        return 1

if __name__ == '__main__':
    # from pipedata.base import index_file_flush

    TrackedFile.VERBOSE=0
    print('START' + 20*"-")
    # symout()
    # print(symout())
    index._root()
    # .input_kw['make_combined']['OUT'].open('r').read())
    index.index_file_flush()
    print('END' + 20*"-")
    
    import dill
    import json
    print json.dumps(dill.load(open(index.path)),indent=4)

