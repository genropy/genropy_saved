# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):

    def main_root(self,pane,**kwargs):
        pane.div('ciao')
        pane.script("""window.addEventListener("message", function(e){console.log(e.data)}, false);""")
