#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class GnrCustomWebPage(object):
    css_requires='warh'
    def windowTitle(self):
         return 'Warhammer RPG'
         
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        center = bc.contentPane(region='center',_class='immaginona')
        box = center.div(nodeId='myMenu',_class='boxscelte')
        box.dataController("genro.dom.effect('myMenu','fadeIn',{duration:2500})",_onStart=True)
        box.a('Entra',href='warh/personaggi',font_size='30px')