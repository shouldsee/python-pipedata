from tests.test_base import SharedCases as SharedObject
import unittest
import os

from pipedata.master_node import MasterNode
import inspect,textwrap
import random
RINT = int(10 * random.random())
RINT = 0



def _writeFunc(func, fn,RINT=RINT):
    s = 'RINT=%r\n'%RINT
    s += textwrap.dedent('\n'.join(inspect.getsource(func).splitlines()[1:]))

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
            fn = _writeFunc(stage2_func, d2/'../stage2/pipe.py')
            index = base.PipeRunner(fn,fn).pipe.index
            self.assertEquals('1024b1024b1024b1024b1024b\n'*RINT,  index.node_dict['main']().returned)
            # index.sync()
            pass
        return

    def test_migrate(self):
        tester = self
        base = self.base
        with (base.test_init()) as stage1:
            fn  =_writeFunc(stage2_func, stage1 / '../stage2/pipe.py')
            fn  =_writeFunc(stage3_func, stage1 / '../stage3/pipe.py')
            index = base.PipeRunner( fn,fn ).pipe.index
            index.sync()
            self.assertEquals(
                '1a1a1a1a1a\n1a1a1a1a1a1a1a1a1a1a\n1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a\n'*RINT,  
                open(index.node_dict['remote']['OUT']().realpath(),'r').read())
                # .returned)

                # index.node_dict['main']().returned)
            # index.sync()
            # assert 0,index.node_dict.keys()
            # self.assertEquals('1b1a1a1a1a\n'*RINT,  index.node_dict['main']().returned)
        pass


def stage2_func(RINT):
    import os,sys
    from pipedata.types import IndexNode
    from pipedata.types import SelfSlaveFile, MasterNode
    from pipedata.types import RemoteNode
    index = IndexNode()
    RemoteNode(index, remote_path='../stage1/pipe.py',remote_name='out5')
    ##import imp
    ##index.node_dict['out5'] = imp.load_source('aaaapipe', '../stage1/pipe.py').index.node_dict['out5']

    @MasterNode.from_func(index,)
    def main(s,(out5,),
        ):
        print ("[result]",out5(),out5())
        s = (open(out5()['OUT'].realpath(),"r").read())
        return s * RINT

    if __name__ == '__main__':
        index.main()


def stage3_func(RINT):
    import os,sys
    from pipedata.types import IndexNode
    from pipedata.types import SelfSlaveFile, SlaveFile
    from pipedata.types import MasterNode
    from pipedata.types import RemoteNode
    index = IndexNode()
    RemoteNode(index, remote_path='../stage1/pipe.py',remote_name='make_combined')
    ##import imp
    ##index.node_dict['out5'] = imp.load_source('aaaapipe', '../stage1/pipe.py').index.node_dict['out5']

    @MasterNode.from_func(index,{
        'OUT':SlaveFile(index,'remote.txt',)
        })
    def remote(self,(make_combined,),
        ):
        with open(self['OUT'].realpath(),'w') as f:
            f.write( RINT*open( make_combined['OUT'].realpath(),"r").read())

    @MasterNode.from_func(index,{})
    def main(s,(remote,),
        ):
        s = (open(remote['OUT'].realpath(),"r").read())
        return s

    if __name__ == '__main__':
        index.main()