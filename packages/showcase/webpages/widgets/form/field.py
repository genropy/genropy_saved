#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        cont = root.contentPane(margin='1em',padding='10px')
        fb=cont.formBuilder(datapath='myform')
        fb.field('showcase.cast.person_id',lbl='Star name',width='15em',zoom=False)