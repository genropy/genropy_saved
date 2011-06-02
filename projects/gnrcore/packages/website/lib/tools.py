#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


def codeToPath(self, folder):
    try:
        if folder:
            return '/'+folder['code'].replace('.','/')+'/'
    except:
        return '/'+folder.replace('.','/')+'/'
    return ''