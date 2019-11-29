
# import pymisca.ext as pyext
import subprocess
def t1():
    test_expect = '+ mkdir -p tests\n+ ln pipedata.py tests -f\n+ rm -f tests/test.index tests/out10.txt tests/out15.txt tests/out5.txt\n+ echo 1\n+ echo a\n+ python2 tests/example_string_short.py\nSTART--------------------\nRUNNING:<Node with func:make_combined>\nRUNNING:<Node with func:out5>\nRUNNING:<Node with func:out10>\nRUNNING:<Node with func:out15>\n1a1a1a1a1a\n1a1a1a1a1a1a1a1a1a1a\n1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a\n\nEND--------------------\n+ python2 tests/example_string_short.py\nSTART--------------------\nSKIPPING:<Node with func:make_combined>\n1a1a1a1a1a\n1a1a1a1a1a1a1a1a1a1a\n1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a\n\nEND--------------------\n+ echo 2\n+ echo b\n+ python2 tests/example_string_short.py\nSTART--------------------\nRUNNING:<Node with func:make_combined>\nRUNNING:<Node with func:out5>\nRUNNING:<Node with func:out10>\nRUNNING:<Node with func:out15>\n2b2b2b2b2b\n2b2b2b2b2b2b2b2b2b2b\n2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b\n\nEND--------------------'


    test_cmd  = '''
    set -x
    exec 2>&1

    mkdir -p tests
    ln pipedata.py tests -f 
    rm -f tests/test.index tests/out*.txt

    echo "1"> tests/number.txt; 
    echo a>tests/letter.txt; 
    python2 tests/example_string_short.py


    python2 tests/example_string_short.py

    echo "2">tests/number.txt; 
    echo b>tests/letter.txt; 
    python2 tests/example_string_short.py
    '''
    print repr(subprocess.check_output(test_cmd,shell=1).strip())
    assert subprocess.check_output(test_cmd,shell=1).strip()==test_expect.strip()
t1()