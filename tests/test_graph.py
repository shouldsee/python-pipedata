from tests.test_base import SharedCases as SharedObject
import unittest
import os
# class SharedObject(_SharedObject):
class GraphCase(unittest.TestCase):
    base = SharedObject()
    # _base
    def test_update(self):
        tester = self
        base = self.base
        PipeRunner = base.PipeRunner

        with (base.test_init()).makedirs_p() as d2:
            base._shell('''
echo 1024> tests-number.txt
echo b> tests-letter.txt
    ''')
            # index=  base.PipeRunner('pipe','pipe.py')()
            index = base.PipeRunner('pipe','pipe.py').pipe.index
            index.node_dict['make_combined']()
            index.index_file_flush()
            exp = '''
1024b1024b1024b1024b1024b
1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b
1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b1024b
            '''.strip()
            got = (open("tests-combined.txt",'r').read().strip())
            assert got== exp,(got,exp,)

            # tester.assertRaises( base.IndexedDiffFileError, PipeRunner('pipe','pipe.py'))
            pass
        return