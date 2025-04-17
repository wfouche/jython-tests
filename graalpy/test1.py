#!/usr/bin/env ./python-run.py
from __future__ import print_function
import json
import sys
import platform

# /// script
# requires-jython = ">=2.7.4"
# requires-java = ">=21"
# ///

def main():
    print("version:", platform.python_version())
    print("args:", sys.argv)
    text = '{"k1": "v1", "k2": "v2", "k3": "v3"}'
    jobj = json.loads(text)
    print(jobj["k2"])

main()
