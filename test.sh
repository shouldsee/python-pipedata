set -e
python test_all.py
#python2 -m unittest discover -s tests
rm -f */*.index && python2 test_all.py BaseCase.test_init && python2 tests/example_bio.py

echo 100 >test_build/tests-number.txt && python2 tests/example_bio.py
