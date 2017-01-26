# -*- coding: UTF-8 -*-

# chartmanager.py
# Created by Francesco Porcari on 2017-01-01.
# Copyright (c) 2017 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent

class StatsPane(BaseComponent):
    py_requires='js_plugins/chartjs/chartjs:ChartPane'
    js_requires='js_plugins/stats/stats'
    css_requires='js_plugins/stats/stats'
