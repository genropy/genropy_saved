#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" Component for referto """

class GnrCustomWebPage(object):
    #py_requires='public:Public'
    
    def main(self, rootBC, **kwargs):
        center = rootBC.contentPane(**kwargs)
        center.data('ppp',True)
        center.radiobutton(value='^ppp',label='Prova radiobutton')
        center.checkbox(value='^ppp',label='Prova checkbox')