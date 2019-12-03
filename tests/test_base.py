# %%writefile test.py
import unittest
unittest.TestCase.assertRaises

import os,sys
#sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
#os.chdir('..')
# from pymisca.tree import getPathStack
import path
import imp
# def getPathStack(x):
#     return path.Path(x[0])

import subprocess
import shutil
import sys

from pipedata.pipe_run import pipe_run
# , _load_source
import imp
import sys
import pipedata.base as pipedata
# from pipedata.types import TrackedDic
from pipedata.types import TrackedDict
from pipedata.base import IndexedDiffFileError,IndexedMissingFileError,ChangedNodeError, ChangedOutputError
# from pipedata.types import IndexedDiffFileError,IndexedMissingFileError,ChangedNodeError
from pipedata.base import IndexNode

from pipedata.types import TrackedFile, InputTrackedFile
import pipedata.types



def _raise(e):
    raise e

import path as pipe
import linecache
class PipeRunner(object):
    def __init__(self, key, fname):
        if fname is None:
            fname
        self.key = key
        key = self.key
        # import pipedata.base as pipedata
        # imp.reload(pipedata)
        fname = os.path.realpath(fname)

#         reload(pipedata) ### class attributes would otherwise be kept  e.g. InputTrackedFile.counter
        linecache.checkcache(fname) #### otherwise one cannot reliably
#         assert 0,linecache.checkcache(fname)
        self.pipe = pipe =  imp.load_source( key, fname)
        # pipe.IndexedDiffFileError = IndexedDiffFileError
        # pipe.IndexedMissingFileError = IndexedMissingFileError
        # pipe.ChangedNodeError = ChangedNodeError        
    def __call__(self,*a,**kw):
        pipe_run(self.pipe.index)
        return self.pipe.index
    

def _dbg():
    import inspect
    pr = PipeRunner('pipe','pipe.py')
    # f = pr.pipe.out10.f
    # _code = f.__code__
    print (_code.co_code.__repr__())
    print (_code.co_consts.__repr__())
    print (inspect.getsource(f))
def _dbgf():        
    import pdb,traceback
    print(traceback.format_exc())
    import traceback
    traceback.print_stack()
    traceback.print_exc()
    pdb.set_trace()        

class SharedCases(object):
    _realpath = path.Path(__file__).dirname().dirname().realpath()
    PipeRunner = PipeRunner
    IndexedDiffFileError = IndexedDiffFileError
    IndexedMissingFileError = IndexedMissingFileError
    ChangedNodeError = ChangedNodeError
    ChangedOutputError = ChangedOutputError
    def realpath(self):
        return self._realpath
    @staticmethod
    def _shell(cmd,shell=True):
        sys.stderr.write("[CMD]%s\n"%cmd)
        return subprocess.check_output(cmd,shell=shell)

    def test_import(self,fn=None):
        fn = fn or 'tests/example_string_short.py'
#         print "[CURR]",os.getcwd()
        pipe = PipeRunner('pipe', fn).pipe
        
        return pipe

    def test_repr_tracked_dict(self):
        # PipeRunner('pipe','pipe.py')
        # __file__ = '__test__'
        # frame_init()
        index = IndexNode(path='__test__.py.index')
        v = TrackedDict( index, 'test',dict(JOB_INDEX=123,))        
        s = repr(v)
        print(s)
        vnew = eval(s)
        assert vnew.data == v.data,(s,v,vnew)
        
    def test_dillable(self):
        pipe = self.test_import('tests/example_string_short.py')
        # reload(pipe)
        import dill
        dill.dumps(pipe,)
        print("[Dillable]")
        

        
    def test_init(self):
        dirname = self.test_import('tests/example_string_short.py').index.make_copy("test_build/stage1",name='pipe.py')
        # dirname = se
        with path.Path(dirname) as d:
            print ( self._shell('''
    echo "1"> tests-number.txt; 
    echo a>tests-letter.txt; 
            '''.format(**locals()))    )
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pipe = PipeRunner('pipe','pipe.py')()
            print (open(pipe._symbolicRootNode.input_kw['make_combined']['OUT'].path,'r').read()    )
        return dirname
    # def test_init2(self):

    def make_index_diff(self):
    # def test_indexedDiffFile(self):
        with path.Path(self.test_init()).makedirs_p() as d:
            self._shell('''
touch tests-out5.txt
''')
            self.assertRaises( IndexedDiffFileError, PipeRunner('pipe','pipe.py'))
            pass
        with path.Path(self.test_init()).makedirs_p() as d:
            self._shell('''
echo 123> tests-out10.txt
''')
            # PipeRunner('pipe','pipe.py')()
            self.assertRaises( IndexedDiffFileError, PipeRunner('pipe','pipe.py'))
            pass
        return

    def test_indexedMissingFile(self):
        with (self.test_init()).makedirs_p().realpath() as d:
            # PipeRunner('pipe','pipe.py')()
            # PipeRunner('pipe','pipe.py')()
            self._shell('''
rm tests-out5.txt             
''')
            # PipeRunner('pipe','pipe.py')()
            # try:
            #     PipeRunner('pipe','pipe.py')()
            # except Exception as e:
            #     assert 0
            # finally:
            #     assert 0

               # print("DONE")
            # except Exception as e:
            #     _dbg()

            self.assertRaises( ChangedOutputError, PipeRunner('pipe','pipe.py'))
            pass
        return

    def test_tracked_dict_indexed_diff(self):
        with path.Path(self.test_init()).makedirs_p() as d:
            class index_diff_error(Exception):
                pass
            def getPr():
                pr =  PipeRunner('pipe','pipe.py')
                pr.pipe.TrackedDict._hook_indexed_diff_file = lambda self: _raise(index_diff_error())
                return pr
            with open("pipe.py",'a+') as f:
                
                f.write(r'''
_p = TrackedDict(index, data={"a":1,"foo":"why am i here?"} , name='paramDict')

''')


            # pr = getPr()
            self.assertRaises( index_diff_error, getPr() )

    class index_diff_error(Exception):
        pass
    def getPr(self):
        index_diff_error = self.index_diff_error
        pr =  PipeRunner('pipe','pipe.py')
        # pr.pipe.MasterNode._hook_indexed_diff_file = lambda self: _raise(index_diff_error())
        pr.pipe.MasterNode._hook_changed_record = lambda s,ccode,cinput:(
            _raise(index_diff_error()) if (True,False)==(ccode,cinput) else None)
        # pr.pipe.MasterNode._hook_changed_record = lambda s,ccode,cinput:(
        #     _raise(index_diff_error()) if (False,True)==(ccode,cinput) else None)        
        return pr

    def test_changedNode(self):
        with path.Path(self.test_init()).makedirs_p() as d:
            getPr = self.getPr
            pr = getPr()()

    def _test_changedNode(self):
        with path.Path(self.test_init()).makedirs_p() as d:
            getPr = self.getPr
            pr = getPr()()


            with open("pipe.py",'a+') as f:
                
                f.write(r'''


### changed 10 to 25
@MasterNode.from_func(index,{
    "OUT":TrackedFile(index,"tests-out10.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out10(  self, (numberFile, letterFile),):
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with open(self['OUT']().path,'w') as f:
        f.write( 25 * (number+letter)+'\n')
    return
''')
            
#             _dbg()
            pr = getPr()
    
#             for k,v in pr.pipe._symbolicRootNode.input_kw.items():
#                 print k,v.func_orig.func_code
#             assert 0
            self.assertRaises( index_diff_error, getPr() )

#             with open("pipe.py",'a+') as f:
#                 f.write(r'''
# ### add dependency on dummy file
# dummyFile = InputTrackedFile(index,'test-dummy.txt')
# @MasterNode.from_func(index,{
#     "OUT":TrackedFile(index,"tests-out10.txt"),
# #     "BAM":TrackedFile( "test.fastq.bam"  )
# })
# def out10(  s, (numberFile, letterFile,  dummyFile) ):

#     number = open( numberFile().path, 'r').read().strip()
#     letter = open( letterFile().path, 'r').read().strip()
#     with open(self['OUT']().path,'w') as f:
#         f.write( 10 * (number+letter)+'\n')
#     return
# ''')
#             self.assertRaises( index_diff_error, getPr() )
        
            #### synonymous_code_change
    def test_code_syno_change(self):
#         assert 0
        class myError(Exception):
            pass
        def getPr():
            pr =  PipeRunner('pipe','pipe.py')
            pr.pipe.MasterNode._hook_indexed_diff_file = lambda self:_raise(myError("%s"%self))
            return pr        
        
        with path.Path(self.test_init()).makedirs_p() as d:
            with open("pipe.py",'a+') as f:
                f.write(r'''
@MasterNode.from_func(index,{{
    "OUT":TrackedFile(index,"tests-out10.txt"),
}})
def out10(  self, (numberFile, letterFile),):
    ###
    "some random comments"
    12334545
    
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with open(self['OUT']().path,'w') as f:
        f.write( 10 * (number+letter)+'\n')
    return
                '''.format(
                    doc = '',
#                     doc="'''docstirng'''"
                ),)

#             pr =  PipeRunner('pipe','pipe.py')

            pr = getPr()
            pr()

        pass


    def test_changedVal(self):
        # dirname = self.make_copy()
        dirname = self.test_init()
        with path.Path(dirname) as d:
            print (self._shell('''
    echo "1"> tests-number.txt; 
    echo a>tests-letter.txt; 
            '''.format(**locals()))  )
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            # pipe.Node.OLD = 0
            pipe.TrackedFile.VERBOSE = 0

#             OLD = 1
            pipe = pr()
            print (open(pipe._symbolicRootNode.input_kw['make_combined']['OUT'].path,'r').read()    )
            
#             return
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            # pipe.MasterNode.OLD = 0

#             pipe.TrackedFile.VERBOSE = 0
#             pipe.TrackedFile.HOOKS_ENABLED_LIST=[]
            
#             self._shell('''
# rm tests-out5.txt             
# ''')        
#             nodes = pipe.index._symbolicRootNode.input_kw.values()
#             [node.changed for node in nodes]
#             [[sys.stdout.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
            
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            # pipe.MasterNode.OLD = 0
            pipe.TrackedFile.VERBOSE = 0
            pipe.TrackedFile.HOOKS_ENABLED_LIST=[]
            
            self._shell('''
touch tests-letter.txt             
''')        
            nodes = pipe.index._symbolicRootNode.input_kw.values()
            [node.changed for node in nodes]
#             [[sys.stdout.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
            [[sys.stderr.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
        
#             pr.pipe
#             print pipe._symbolicOutputNode().input_kw['make_combined']['OUT'].open('r').read()    
        return dirname
    def test_level_stream(self):
        import pipedata.types
        reload(pipedata.types)
        from pipedata.types import TrackedFile, InputTrackedFile
        # __file__ = 'test_temp.py'
        # frame_init()
        index = IndexNode('__temp.py.index')
        out5 = InputTrackedFile(index,"a.txt","tt1")
        File1 = InputTrackedFile(index,"tests-out5.txt","tt2")
        File2 = InputTrackedFile(index, "tests-outxx.txt","tt3")
        out5.merge(File1)
        out5.merge(File2)
        # File2.merge(out5)
        print (out5.level_stream)
        print (File1.level_stream)
        print (File2.level_stream)
        assert out5.level_stream == File1.level_stream ==File2.level_stream == {out5,File1,File2}

        out5 = InputTrackedFile(index,"a.txt","t1")
        File1 = InputTrackedFile(index,"tests-out5.txt","t2")
        File2 = InputTrackedFile(index, "tests-outxx.txt","t3")

        out5.merge(File1)
        # out5.merge(File2)
        File2.merge(out5)
        print (out5.level_stream)
        print (File1.level_stream)
        print (File2.level_stream)
        assert out5.level_stream == File1.level_stream ==File2.level_stream == {out5,File1,File2}

#         return self.test_dillable()
class BaseCase( unittest.TestCase,SharedCases,):
    pass

import pdb
import traceback
def debugTestRunner(post_mortem=None):
    """unittest runner doing post mortem debugging on failing tests"""
    if post_mortem is None:
        post_mortem = pdb.post_mortem
    class DebugTestResult(unittest.TextTestResult):
        def addError(self, test, err):
            # called before tearDown()
            traceback.print_exception(*err)
            post_mortem(err[2])
            super(DebugTestResult, self).addError(test, err)
        def addFailure(self, test, err):
            traceback.print_exception(*err)
            post_mortem(err[2])
            super(DebugTestResult, self).addFailure(test, err)
    return unittest.TextTestRunner(resultclass=DebugTestResult)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
#     if "-1" in sys.argv:
#         del sys.argv[sys.argv.index('-1')]
#         runner.run(testCase())
#     else:
    if "--debug" in sys.argv:
        del sys.argv[sys.argv.index('--debug')]
        unittest.main(testRunner = debugTestRunner())
    else:
        unittest.main()

#     unittest.findTestCases(__main__).debug()
