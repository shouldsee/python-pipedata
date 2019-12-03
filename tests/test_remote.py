import unittest
import path
import os,sys

# import tests
# print tests.__file__
from tests.test_base import BaseCase, debugTestRunner
from tests.test_base import SharedCases as _SharedObject



class SharedObject(_SharedObject):
    # def test_a(self):
    #     # return self.test_init()
    #     return self.base.test_init()
    def test_stage2(self):
        d1 = self.test_init()
        dirname = self.test_import('tests/example_stage2.py').index.make_copy("test_build/stage2",name='pipe.py')
        # assert 0,type(dirname)
        with dirname:
            index = self.PipeRunner('pipe','pipe.py')()
            print (index.records_cached.items())
        return dirname

        
    def _(self):
        with path.Path(dirname) as d:
            print ( self._shell('''
echo "1"> tests-number.txt; 
echo a>tests-letter.txt; 
            '''.format(**locals()))    )
#             import pipe
#             pipe= imp.load_source( 'pipe', 'pipe.py')
#             pipe_run(pipe)
            pipe = self.PipeRunner('pipe','pipe.py')()
            print (open(pipe._symbolicRootNode.input_kw['make_combined']['OUT'].path,'r').read()    )
        return dirname

# from pymisca.ext import jf2
class ThisCase(unittest.TestCase, ):
    base = SharedObject()
    def test_stage2(self):
        return self.base.test_stage2()

    def test_index_diff(self):
        tester = self
        base = self.base
        PipeRunner = base.PipeRunner

        with base.test_stage2().realpath() as d:
            with base.realpath() as d1:
                with (base.test_init()).makedirs_p() as d2:
                    pass
                    base._shell(('''
#                    echo {{d2.realpath()}};
echo 123> tests-out5.txt
                            '''))
            assert os.getcwdu() == d.realpath(), (os.getcwdu(), )
            tester.assertRaises( base.ChangedOutputError, PipeRunner('pipe','pipe.py'))
            pass
        return
    def test_index_missing(self):
        tester = self
        base = self.base
        PipeRunner = base.PipeRunner

        with base.test_stage2().realpath() as d:
            with base.realpath() as d1:
                with (base.test_init()).makedirs_p() as d2:
                    pass
                    base._shell(('''
#                    echo {{d2.realpath()}};
rm tests-out5.txt
                            '''))
            assert os.getcwdu() == d.realpath(), (os.getcwdu(), )
            tester.assertRaises( base.ChangedOutputError, PipeRunner('pipe','pipe.py'))
            pass
        return

    def test_update(self):
        tester = self
        base = self.base
        PipeRunner = base.PipeRunner

        with base.test_stage2().realpath() as d:
            with base.realpath() as d1:
                with (base.test_init()).makedirs_p() as d2:
                    base._shell('''
        echo 1024> tests-number.txt
        ''')
            assert os.getcwdu() == d.realpath(), (os.getcwdu(), )                    
            # assert os.getcwdu() == d.realpath(), (os.getcwdu(), )
            index = PipeRunner('pipe','pipe.py')()
            exp = "1024a1024a1024a1024a1024a\n"
            got = index._symbolicRootNode.input_kw['main'].returned 
            assert got== exp,(got,exp,)
            # tester.assertRaises( base.IndexedDiffFileError, PipeRunner('pipe','pipe.py'))
            pass
        return

del BaseCase

if __name__ == '__main__':
    if "--debug" in sys.argv:
        del sys.argv[sys.argv.index('--debug')]
        unittest.main(testRunner = debugTestRunner())
    else:
        unittest.main()
