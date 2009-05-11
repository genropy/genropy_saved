#!/usr/bin/env python
# encoding: utf-8

import sys, os
from gnr.app.gnrapp import GnrApp

if __name__ == '__main__':
    app = GnrApp(os.getcwd())
    app.packages['cddb'].importFolder(sys.argv[1])