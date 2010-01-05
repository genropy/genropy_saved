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

from gnr.core.gnrstring import templateReplace
from gnr.web.gnrwebpage import BaseComponent
from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlSaveChangesException,GnrSqlExecutionException
from gnr.core.gnrbag import Bag

class TableHandler(BaseComponent):
    py_requires='foundation/tablehandler'