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
import imp
import sys
from pipedata import IndexedDiffFileError,IndexedMissingFileError
# import os as pip/e
def _shell(cmd,shell=True):
    sys.stderr.write("[CMD]%s\n"%cmd)
    return subprocess.check_output(cmd,shell=shell)
class PipeRunner(object):
    def __init__(self, key='pipe'):
        self.key = key
    def __call__(self,*a,**kw):
        key = self.key
        pipe = imp.load_source( key, key +'.py')
        pipe_run(pipe)
        return pipe

class test(unittest.TestCase):
    def test_import(self):
        pass
#         print "[CURR]",os.getcwd()
        pipe = imp.load_source('pipe','tests/example_string_short.py')
        
#         import tests.example_string_short as pipe
#         pipe.__file__ = os.path.realpath(pipe.__file__)
        return pipe
        
    def test_dillable(self):
        pipe = self.test_import()
#         imp/reload(pipe)
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
            pipe = PipeRunner()()
            print pipe._symbolicOutputNode().input_kw['make_combined']['OUT'].open('r').read()    
        return dirname
    
    def test_indexedDiffFile(self):
        with path.Path(self.test_1()).makedirs_p() as d:
            _shell('''
touch tests-out5.txt
''')
            self.assertRaises( IndexedDiffFileError, PipeRunner())
            pass
        return
    def test_indexedMissingFile(self):
        with path.Path(self.test_1()).makedirs_p() as d:

            _shell('''
rm tests-out5.txt             
''')
            self.assertRaises( IndexedMissingFileError, PipeRunner())
            pass
        return
if __name__ == '__main__':
#     runner = unittest.TextTestRunner()
#     runner.run(test())
    unittest.main()