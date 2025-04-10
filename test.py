from __future__ import print_function
import sys

##DEPS io.leego:banana:2.1.0
##JYTHON 2.7.4
##JAVA 21

import io.leego.banana.BananaUtils as BananaUtils
import io.leego.banana.Font as Font


def main():
    print(sys.argv)

    text0 = "Jython 2.7"
    text1 = BananaUtils.bananaify(text0, Font.STANDARD)

    print(text1)

main()
