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

