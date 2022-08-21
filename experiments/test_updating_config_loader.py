"""
Tests for UpdatingConfigLoader()

Author: Tazard 2021
Compatibility: Python3
"""

import os
from updating_config_loader import UpdatingConfigLoader

TEST_URL = "https://gist.githubusercontent.com/tazard/ecdd907a01b1c35d46347f6c8557ee65/raw/b41bba2ed414701fbce5d235a62879479ea673bb/config_dummy.json"
TEST_URL_BAD_JSON = "https://gist.githubusercontent.com/tazard/d0f3f90014b38353249d6d55215bacc2/raw/91324614d9ddb6a057a8f6dc7377dfb56957ea58/config_dummy_bad_json.json"
LOCAL_FILE = "config/config_test.json"

def remove_existing():
    if os.path.exists(LOCAL_FILE):
        print(" test - deleting existing LOCAL_FILE")
        os.remove(LOCAL_FILE)

def construct():
    o = UpdatingConfigLoader(LOCAL_FILE, TEST_URL)
    return o.contents

def construct_bad_url():
    o = UpdatingConfigLoader(LOCAL_FILE, "bad")
    return o.contents

def construct_bad_json_response():
    o = UpdatingConfigLoader(LOCAL_FILE, TEST_URL_BAD_JSON)
    return o.contents

def construct_bad_path():
    o = UpdatingConfigLoader('/a/b/c/d/e/f.txt', TEST_URL)
    return o.contents

def construct_bad_local_and_remote():
    o = UpdatingConfigLoader('bad', 'bad')
    return o.contents

def change_bad_json():
    with open(LOCAL_FILE, 'w') as f:
        f.write("\nbad data\n")

def change_ok_json():
    with open(LOCAL_FILE, 'w') as f:
        f.write('{"some data": 0}')

def check(first, second):
    if first != second:
        raise Exception("Does not match\nFirst:\n" + str(first) + "\nSecond:\n" + str(second))
    print(" test - Pass")


def main():
    print("\n test - Prepare for testing")
    remove_existing()

    print("\n test - Construction when no local file exists")
    ref = construct()

    print("\n test - Construction when identical local file exists")
    sec = construct()
    check(ref, sec)

    print("\n test - Construction when bad local file exists")
    change_bad_json()
    sec = construct()
    check(ref, sec)

    print("\n test - Construction when different but ok local file exists")
    change_ok_json()
    sec = construct()
    check(ref, sec)

    print("\n test - Construction URL bad")
    sec = construct_bad_url()
    check(ref, sec)

    print("\n test - Bad local path")
    try:
        construct_bad_path()
    except:
        print(' test - Caught bad path exception')
        print(' test - Pass')
    else: 
        raise Exception('test failed')

    print("\n test - Bad JSON Response")
    sec = construct_bad_json_response()
    check(ref, sec)

    print("\n test - Bad local and remote")
    try:
        sec = construct_bad_local_and_remote()
    except:
        print(' test - Caught bad local and remote')
        print(' test - Pass')
    else: 
        raise Exception('test failed')

if __name__ == "__main__":
    main()