#!/usr/bin/env ./python-run.py
from __future__ import print_function
import sys

# /// jbang
# requires-graalpy = ">=24.2.1"
# requires-java = ">=21"
# dependencies = [
#   "io.leego:banana:2.1.0",
# ]
# ///
import java

#import io.leego.banana.BananaUtils as BananaUtils
#import io.leego.banana.Font as Font

BananaUtils = java.type('io.leego.banana.BananaUtils')
Font = java.type('io.leego.banana.Font')

def main():
    print(sys.argv)

    text0 = "GraalPython 24.2.1"
    text1 = BananaUtils.bananaify(text0, Font.STANDARD)

    print(text1)

main()
