#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

"""
DOJO 11
"""
import os

from gnr.web.gnrbaseclasses import BaseComponent

class TableHandler(BaseComponent):
    py_requires='standard_tables/tablehandler'
    
class TableHandlerLight(BaseComponent):
    py_requires='standard_tables/tablehandler_light'