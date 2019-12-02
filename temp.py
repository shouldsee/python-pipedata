import unittest

class CommonTests(object):
    def testCommon(self):
        print 'Calling BaseTest:testCommon'
        value = 5
        self.assertEquals(value, 5)

class SubTest1(unittest.TestCase, CommonTests):

    def testSub1(self):
        print 'Calling SubTest1:testSub1'
        sub = 3
        self.assertEquals(sub, 3)


class SubTest2(unittest.TestCase, CommonTests):

    def testSub2(self):
        print 'Calling SubTest2:testSub2'
        sub = 4
        self.assertEquals(sub, 4)

if __name__ == '__main__':
    unittest.main()
