#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Examples & Tutorials """

from gnr.core.gnrbag import Bag



class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #layout = self.rootLayoutContainer(root,padding='2px',height='100%')
        #root.data('cliente',Bag(dict(nome="Mario",cognome="Rossi")))
        lc = root.LayoutContainer(height='100%')
        top=lc.contentpane(layoutAlign="top",height="5%",background_color="gray")
        top2=lc.contentpane(layoutAlign="top",height="5%",background_color="black")
        left=lc.contentpane(layoutAlign="left",width="30%",background_color="pink")

        left.tree(storepath="*D",inspect="shift",label='Datasource')

        tb=lc.tabcontainer(layoutAlign="client",height="100%")
        tab1=tb.contentpane(title="tab1")
        tab2=tb.contentpane(title="tab2")

        myform=tab1.formbuilder(cols=2,lblpos="T")
        myform.textbox(lbl="nome",datasource="cliente.nome",default='mario')    #datasource si riferisce sempre alla memory di genro lato client
        myform.textbox(lbl="cognome",datasource="cliente.cognome",default='rossi')
        myform.button(lbl="submitbutton",label="Click me",action="alert('hai scritto:'+genro.getData('cliente.nome'))")
    
    #main=lc.contentpane(layoutAlign="client",background_color="lime")
    #main.span("Che bello!")
    
    #root.span("Hello word");





