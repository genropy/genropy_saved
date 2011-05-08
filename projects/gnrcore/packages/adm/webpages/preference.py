#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


class GnrCustomWebPage(object):
    maintable = 'adm.preference'
    py_requires = """public:Public"""

    def pageAuthTags(self, **kwargs):
        return 'user'

    def windowTitle(self):
        return '!!Preference panel'

    def main(self, rootBC, **kwargs):
        mainbc, top, bottom = self.pbl_rootBorderContainer(rootBC, '!!Preference')
