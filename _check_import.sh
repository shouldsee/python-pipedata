grep -rnw "import" . | grep -v "#" | grep -v pipedata | grep -v archive | grep -v "tests\." | grep -v "os\|sys\|path" 
