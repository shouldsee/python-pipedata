import unittest
unittest.TestCase.assertRaises

import os
# from pymisca.tree import getPathStack
import path
# def getPathStack(x):
#     return path.Path(x[0])

import subprocess
import shutil
import sys

from pipe_run import pipe_run
# , _load_source
import imp
import sys
import pipedata
from pipedata import IndexedDiffFileError,IndexedMissingFileError
# import os as pip/e
def _shell(cmd,shell=True):
    sys.stderr.write("[CMD]%s\n"%cmd)
    return subprocess.check_output(cmd,shell=shell)

import path as pipe
class PipeRunner(object):
    def __init__(self, key, fname):
        if fname is None:
            fname
        self.key = key
        key = self.key
        import pipedata
        reload(pipedata)
        pipedata.IndexedDiffFileError = IndexedDiffFileError
        pipedata.IndexedMissingFileError = IndexedMissingFileError
#         reload(pipedata) ### class attributes would otherwise be kept  e.g. InputTrackedFile.counter
        self.pipe = imp.load_source( key, fname)
        
    def __call__(self,*a,**kw):
        pipe_run(self.pipe)
        return self.pipe

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
            print _shell('''
    echo "1"> tests-number.txt; 
    echo a>tests-letter.txt; 
            '''.format(**locals()))    
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pipe = PipeRunner('pipe','pipe.py')()
            print pipe._symbolicRootNode.input_kw['make_combined']['OUT'].open('r').read()    
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
    
    def test_changedVal(self):
        dirname = self.make_copy()
        with path.Path(dirname) as d:
            print _shell('''
    echo "1"> tests-number.txt; 
    echo a>tests-letter.txt; 
            '''.format(**locals()))    
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pr = PipeRunner('pipe','pipe.py')
            pipe = pr.pipe
            pipe.Node.OLD = 1
            pipe.TrackedFile.VERBOSE = 0

#             OLD = 1
            pipe = pr()
            print pipe._symbolicRootNode.input_kw['make_combined']['OUT'].open('r').read()    
            
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
            print "[WTF]"
            [[sys.stderr.write("%s\n"%[node,node.changed,node.changed_upstream]),node.changed][1] for node in nodes]
#             print nodes
        
#             pr.pipe
#             print pipe._symbolicOutputNode().input_kw['make_combined']['OUT'].open('r').read()    
        return dirname

#         return self.test_dillable()
    
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
#     if "-1" in sys.argv:
#         del sys.argv[sys.argv.index('-1')]
#         runner.run(testCase())
#     else:
    unittest.main()