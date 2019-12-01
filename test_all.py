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
import pipedata._pipedata as pipedata
from pipedata._pipedata import IndexedDiffFileError,IndexedMissingFileError,ChangedNodeError
# import os as pip/e
def _shell(cmd,shell=True):
    sys.stderr.write("[CMD]%s\n"%cmd)
    return subprocess.check_output(cmd,shell=shell)

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
        import pipedata.types as pipedata
        imp.reload(pipedata)
        pipedata.IndexedDiffFileError = IndexedDiffFileError
        pipedata.IndexedMissingFileError = IndexedMissingFileError
        pipedata.ChangedNodeError = ChangedNodeError
#         reload(pipedata) ### class attributes would otherwise be kept  e.g. InputTrackedFile.counter
        linecache.checkcache(fname) #### otherwise one cannot reliably
#         assert 0,linecache.checkcache(fname)
        self.pipe = imp.load_source( key, fname)
        
    def __call__(self,*a,**kw):
        pipe_run(self.pipe)
        return self.pipe
    
# class index_diff_error(Exception):
#     pass

class testCase(unittest.TestCase):
    def test_import(self):
        pass
#         print "[CURR]",os.getcwd()
        pipe = PipeRunner('pipe','tests/example_string_short.py').pipe
        
#         import tests.example_string_short as pipe
#         pipe.__file__ = os.path.realpath(pipe.__file__)
        return pipe
        
    def test_dillable(self):
        pipe = self.test_import()
        import dill
        dill.dumps(pipe,)
        print("[Dillable]")
        
    def make_copy(self, name =None):
        pipe = self.test_import()
        if name is None:
            name = 'test_build'
            
        subprocess.check_output("mkdir -p {name}/ && rm -fr {name}/*".format(**locals())
                                ,shell=1)
#         modpath = name+'/pipe.py'
        d = path.Path(name)

        fn = pipe.__file__.replace('.pyc','.py')
        shutil.copy2(fn,d/"pipe.py" )
#         shutil.copy2('tests/example_string_short.py'.replace('.pyc','.py'), modpath )
        import pipedata
        fn = pipedata.__file__.replace('.pyc','.py')
        shutil.copy2( fn, d/"pipedata.py")
        
        return name
        
    def test_1(self):
        dirname = self.make_copy()
        with path.Path(dirname) as d:
            print (_shell('''
    echo "1"> tests-number.txt; 
    echo a>tests-letter.txt; 
            '''.format(**locals()))    )
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pipe = PipeRunner('pipe','pipe.py')()
            print (pipe._symbolicRootNode.input_kw['make_combined']['OUT'].open('r').read()    )
        return dirname
    
    def test_indexedDiffFile(self):
        with path.Path(self.test_1()).makedirs_p() as d:
            _shell('''
touch tests-out5.txt
''')
            self.assertRaises( IndexedDiffFileError, PipeRunner('pipe','pipe.py'))
            pass
        return
    def test_indexedMissingFile(self):
        with path.Path(self.test_1()).makedirs_p() as d:

            _shell('''
rm tests-out5.txt             
''')
            self.assertRaises( IndexedMissingFileError, PipeRunner('pipe','pipe.py'))
            pass
        return
    
    def test_changedNode(self):
        with path.Path(self.test_1()).makedirs_p() as d:
            def _dbg():
                import inspect
                pr = PipeRunner('pipe','pipe.py')
                f = pr.pipe.out10.f
                _code = f.__code__
                print (_code.co_code.__repr__())
                print (_code.co_consts.__repr__())
                print (inspect.getsource(f))

            class index_diff_error(Exception):
                pass
#             class 

            def getPr():
                pr =  PipeRunner('pipe','pipe.py')
                pr.pipe.RawNode._hook_indexed_diff_file = lambda self: _raise(index_diff_error())
                return pr

            with open("pipe.py",'a+') as f:
                
                f.write(r'''


### changed 10 to 25
@Node.from_func({
    "OUT":TrackedFile("tests-out10.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out10(  self, numberFile, letterFile ):
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with self.output_kw['OUT'].open("w") as f:
        f.write( 25 * (number+letter)+'\n')
    return
''')
            
#             _dbg()
            pr = getPr()
    
#             for k,v in pr.pipe._symbolicRootNode.input_kw.items():
#                 print k,v.func_orig.func_code
#             assert 0
            self.assertRaises( index_diff_error, getPr() )
            with open("pipe.py",'a+') as f:
                f.write(r'''
### add dependency on dummy file
dummyFile = InputTrackedFile('test-dummy.txt')
@Node.from_func({
    "OUT":TrackedFile("tests-out10.txt"),
#     "BAM":TrackedFile( "test.fastq.bam"  )
})
def out10(  s, numberFile, letterFile,  dummyFile ):

    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with self.output_kw['OUT'].open("w") as f:
        f.write( 10 * (number+letter)+'\n')
    return
''')
            self.assertRaises( index_diff_error, getPr() )
        
            #### synonymous_code_change
    def test_code_syno_change(self):
#         assert 0
        class myError(Exception):
            pass
        def getPr():
            pr =  PipeRunner('pipe','pipe.py')
            pr.pipe.RawNode._hook_indexed_diff_file = lambda self:_raise(myError())
            return pr        
        
        with path.Path(self.test_1()).makedirs_p() as d:
            with open("pipe.py",'a+') as f:
                f.write(r'''
@Node.from_func({{
    "OUT":TrackedFile("tests-out10.txt"),
}})
def out10(  self, numberFile, letterFile ):
    ###
    
    "some random comments"
    12334545
    
    number = open( numberFile().path, 'r').read().strip()
    letter = open( letterFile().path, 'r').read().strip()
    with self.output_kw['OUT'].open("w") as f:
        f.write( 10 * (number+letter)+'\n')
    return
                '''.format(
                    doc = '',
#                     doc="'''docstirng'''"
                ),
                       )      
#             pr =  PipeRunner('pipe','pipe.py')

            pr = getPr()
            pr()

        pass


    def test_changedVal(self):
        dirname = self.make_copy()
        with path.Path(dirname) as d:
            print (_shell('''
    echo "1"> tests-number.txt; 
    echo a>tests-letter.txt; 
            '''.format(**locals()))  )
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            pipe.Node.OLD = 1
            pipe.TrackedFile.VERBOSE = 0

#             OLD = 1
            pipe = pr()
            print (pipe._symbolicRootNode.input_kw['make_combined']['OUT'].open('r').read()    )
            
#             return
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            pipe.RawNode.OLD = 0
            pipe.TrackedFile.VERBOSE = 0
            pipe.TrackedFile.HOOKS_ENABLED_LIST=[]
            
            _shell('''
rm tests-out5.txt             
''')        
            nodes = pipe._symbolicRootNode.input_kw.values()
            [node.changed for node in nodes]
            [[sys.stdout.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
            
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            pipe.RawNode.OLD = 0
            pipe.TrackedFile.VERBOSE = 0
            pipe.TrackedFile.HOOKS_ENABLED_LIST=[]
            
            _shell('''
rm tests-letter.txt             
''')        
            nodes = pipe._symbolicRootNode.input_kw.values()
            [node.changed for node in nodes]
#             [[sys.stdout.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
            [[sys.stderr.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
        
#             pr.pipe
#             print pipe._symbolicOutputNode().input_kw['make_combined']['OUT'].open('r').read()    
        return dirname

#         return self.test_dillable()

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
    unittest.main()
    # unittest.main(testRunner = debugTestRunner())
#     unittest.findTestCases(__main__).debug()
