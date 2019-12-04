# python2 tests/test_all.py BaseCase.test_init
# pip2 install . --user

# find . -name "*.index" -delete
# echo =======
# python2 tests/test_all.py MigrationCase.test_stage2 &> LOG || { echo FAIL1 && exit 1; }
# python2 test_build/stage1/pipe.py --changed-upstream
# python2 test_build/stage2/pipe.py --changed --verbose; echo
# echo ======
# python2 tests/test_all.py MigrationCase.test_stage2_unsynced &> LOG || { echo FAIL2 && exit 1; }
# python2 test_build/stage1/pipe.py --changed-upstream
# python2 test_build/stage2/pipe.py --changed --verbose; echo
# echo =========
# python2 tests/test_all.py MigrationCase.test_stage2_synced  &>LOG||{ echo FAIL3 && exit 1; }
# python2 test_build/stage1/pipe.py --changed-upstream ; echo

# python2 test_build/stage1/pipe.py --changed --verbose; echo
python2 test_build/stage2/pipe.py --changed-upstream; echo
python2 test_build/stage3/pipe.py --changed-upstream; echo
python2 test_build/stage3/pipe.py --tree; echo
python2 test_build/stage1/pipe.py --tree; echo
# python2 test_build/stage1/pipe.py --graph; echo
# python2 test_build/stage1/pipe.py --changed; echo

# python2 test_build/stage2/pipe.py --changed ; echo 
# python2 $PWD/test_build/stage1/pipe.py; echo 
