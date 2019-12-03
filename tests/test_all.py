# %%writefile test.py
import unittest
unittest.TestCase.assertRaises

import os,sys

__file__ = os.path.realpath(__file__)
import path
import imp

# from tests.test_base import BaseCase,debugTestRunner
# from tests.test_remote import ThisCase
# from tests.test_graph import GraphCase
 # as CaseBase
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from tests.test_base import BaseCase,debugTestRunner
from tests.test_remote import ThisCase
from tests.test_graph import GraphCase
from tests.test_migration import MigrationCase
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
