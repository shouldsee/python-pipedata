set -x
exec 2>&1

mkdir -p tests
rm tests/*.txt

# 
ln pipedata.py tests -f 
rm -f tests/*.index
rm -f tests/test.index tests/out*.txt

echo "1"> tests/number.txt; 
echo a>tests/letter.txt; 
python2 tests/example_string_short.py

touch tests/out5.txt
python2 tests/example_string_short.py

rm tests/out5.txt  
### when missing a cached file 
## it needs to be detected and fixed
python2 tests/example_string_short.py

echo something> tests/out5.txt
echo "2">tests/number.txt; 
echo b>tests/letter.txt; 
python2 tests/example_string_short.py