from pipedata.base import RawNode,TrackedFile, InputTrackedFile,  IndexNode
from pipedata.types import TrackedDict
from pipedata.types import MasterNode, SlaveFile, SelfSlaveFile
import os

index = IndexNode()
# print ("[indexFile]",index)

_f1 = SelfSlaveFile( index, 'tests-number.txt',name='numberFile')
_f2 = SelfSlaveFile( index, 'tests-letter.txt',name='letterFile')

@MasterNode.from_func(index,
    {
    "OUT":  SlaveFile(index,  path = "tests-out5.txt"),

})
def out5(  self, (numberFile, letterFile, 
    # paramDict
    ), 
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


@MasterNode.from_func(index,
    {
    "OUT": SlaveFile(index,"tests-out10.txt"),
})
def out10(  self, (numberFile, letterFile), ):
    '''
    some doc
    '''
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with open(self['OUT']().path,'w') as f:
        f.write( 10 * (number+letter)+'\n')
    return


@MasterNode.from_func(index,
    {
    "OUT":SlaveFile(index,"test-combined_short.txt"),
})
def make_combined_short( self, (out5, out15), ):
    lines = []
    [ lines.extend(list(
        open(x()['OUT'].path,'r'))) for x in [out5, out15, ]]
    with open(self['OUT']().path,'w') as f:
        map(f.write,lines)
    return 1

@MasterNode.from_func(index,{
    "OUT":SlaveFile(index,"tests-out15.txt"),
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


@MasterNode.from_func(index,{
    'OUT':SlaveFile(index,'tests-combined.txt')
})
def make_combined( self, (out5, out10, out15,), ):
    lines = []
    [ lines.extend(list(
        open(x()['OUT'].path,'r'))) for x in [out5, out10, out15, ]]    
    with open(self['OUT']().path,'w') as f:
         map(f.write,lines)
    return 1

# @MasterNode.from_func(index,
#     {
#     "OUT":SlaveFile(index,"repeats.txt"),
# })
# def make_repeats( self, (letterFile,dummyFile, ), ):
#     lines = []
#     [ lines.extend(list(
#         open(x()['OUT'].path,'r'))) for x in [out5, out15, ]]
#     with open(self['OUT']().path,'w') as f:
#         map(f.write,lines)
#     return 1


if __name__ == '__main__':
    index.main()
    # print('START' + 20*"-")
    # self = index
    # with self.path.dirname():
    #     [ x() for x in self._symbolicRootNode.input_kw.values()]
    # self.index_file_flush()
    # print('END' + 20*"-")
