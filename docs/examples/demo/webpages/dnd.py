#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """


# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.css(".target {border: 1px dotted gray; width: 300px; height: 300px;padding: 5px;}")
        root.css(".source {border: 1px dotted skyblue;height: 200px; width: 300px;}")
        root.css(".bluesquare {height:50px;width:100%;background-color:skyblue}")
        root.css(".redsquare {height:50px;width:100%;background-color:red}")
        root.css("body {font-size: 12px;}")

        root.h1("A Simple Example")
        x= root.table().tbody().tr().td()
        m=x.div(dojoType="dojo.dnd.Source", jsId="c1", _class="source")
        m.div('Source',)
        m.div( _class="dojoDndItem", dndType="blue").div ('BLUE', _class="bluesquare")
        m.div(_class="dojoDndItem",dndType="red,darkred").div('RED', _class="redsquare")

                    
    def windowTitle(self):
        return 'Simple DnD Example'

 
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()


