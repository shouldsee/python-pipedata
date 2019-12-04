set -e

python $PWD/tests/test_all.py "$@"

#pip2 install . --user
#find . -name "*.index" -delete
bash test_interaction.sh
exit 0

python2 $PWD/tests/test_all.py 
python2 $PWD/tests/test_all.py MigrationCase.test_migrate 
python2 test_build/stage3/pipe.py 
python2 test_build/stage3/pipe.py 

# # find . -name "*.index" -d
# python2 $PWD/tests/test_all.py 
# python2 $PWD/tests/test_all.py MigrationCase.test_migrate 
# python2 test_build/stage3/pipe.py 

#python test_all.py
#python2 -m unittest discover -s tests
#rm -f */*.index && python2 test_all.py Case.test_1 && python2 tests/example_bio.py

#echo 100 >test_build/tests-number.txt && python2 tests/example_bio.py
