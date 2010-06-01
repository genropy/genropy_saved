#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class GnrCustomWebPage(object):
    css_requires='warh'
    def windowTitle(self):
         return 'Warhammer RPG'
         
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        top = bc.contentPane(region='top',_class='titolone')
        # left = bc.contentPane(region='left',width='80px',background='white',splitter=True)
        center = bc.contentPane(region='center',_class='immaginona') # va sempre inserito per ultimo!!
        box = center.div(nodeId='myMenu',_class='boxscelte')
        box.dataController("genro.dom.effect('myMenu','fadeIn',{duration:1000})",_onStart=True)
        box.a('Scheda',href='scheda')
        box.br()
        box.a('Razze',href='razze')
        