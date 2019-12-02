# %%writefile test.py
import unittest
unittest.TestCase.assertRaises

import os,sys

import path
import imp
from tests.test_base import BaseCase,debugTestRunner
from tests.test_remote import ThisCase
 # as CaseBase

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
