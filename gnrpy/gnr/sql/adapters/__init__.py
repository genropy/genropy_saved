#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Genro  
# Copyright (c) 2004 Softwell sas - Milano see LICENSE for details
# Author Giovanni Porcari, Francesco Cavazzana, Saverio Porcari, Francesco Porcari

# Subject: __init__

import os

STANDARD_ENCODING = "UTF-8"
STANDARD_XML_ENCODING = "iso-8859-15"
version_info = (0, 0, 1)
__version__ = "0.0.1"

__all__ = [x.split('.')[0] for x in os.listdir(os.path.dirname(__file__)) if
           (x.startswith('gnr') and x.endswith('.py'))]



#----------------------------------------------------------------------------