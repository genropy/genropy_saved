# -*- coding: UTF-8 -*-

# myindex.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    css_requires = 'grafica'
    
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        center = bc.contentPane(region='center', _class='immagine')