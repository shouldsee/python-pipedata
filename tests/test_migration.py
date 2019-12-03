from tests.test_base import SharedCases as SharedObject
import unittest
import os

import random
RINT = int(100 * random.random())
def _writeStage2(fn,RINT=RINT):
    s = '''
import os,sys
from pipedata.types import IndexNode
from pipedata.types import SelfSlaveFile, MasterNode
from pipedata.types import RemoteNode

index = IndexNode()

import imp
index.node_dict['out5'] = imp.load_source('aaaapipe','../stage1/pipe.py').index.node_dict['out5']

@MasterNode.from_func(index,)
def main(s,(out5,),
    ):
    print ("[result]",out5(),out5())
    s = (open(out5()['OUT'].realpath(),"r").read())
    return s*{RINT}

if __name__ == '__main__':
    print('START' + 20*"-")
    [x() for x in index.node_dict.values()]
    index.index_file_flush()
    print('END' + 20*"-")

'''.format(**locals())
    fn = fn.realpath()
    fn.dirname().makedirs_p()
    assert fn.dirname().exists(),(fn,)
    with open(fn,'w') as f:
        # assert 0,(fn,)
        # .realpath()
        f.write(s)
        return fn
class MigrationCase(unittest.TestCase):
    base = SharedObject()
    # _base
    def test_update(self):
        tester = self
        base = self.base
        with (base.test_init().realpath()).makedirs_p() as d2:
            # assert 0, d2.realpath()
            base._shell('''
echo 1024> tests-number.txt
echo b> tests-letter.txt
    ''')
            _writeStage2(d2/'../stage2/pipe.py')
            index = base.PipeRunner('pipe','../stage2/pipe.py').pipe.index
            self.assertEquals('1024b1024b1024b1024b1024b\n'*RINT,  index.node_dict['main']().returned)
            pass
        return

    def test_migrate(self):
        tester = self
        base = self.base
        with (base.test_init()) as stage1:
            index = base.PipeRunner('rpipe',_writeStage2(stage1 / '../stage2/pipe.py')).pipe.index
            self.assertEquals('1a1a1a1a1a\n'*RINT,  index.node_dict['main']().returned)
            # assert 0,index.node_dict.keys()
            # self.assertEquals('1b1a1a1a1a\n'*RINT,  index.node_dict['main']().returned)
        pass