#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return 'staff'

    def onMain_pbl(self):
        self.pageSource().data('gnr.appmenu', self.getUserMenu())

    def mainLeftContent(self, parentBC, **kwargs):
        leftPane = parentBC.contentPane(width='20%', _class='menupane', **kwargs)
        leftPane = leftPane.div()
        leftPane.tree(id="_gnr_main_menu_tree", storepath='gnr.appmenu', #selected_file='gnr.filepath',
                      labelAttribute='label',
                      hideValues=True,
                      _class='menutree',
                      persist='site',
                      inspect='shift',
                      identifier='#p',
                      getIconClass='return node.attr.iconClass || "treeNoIcon"',
                      getLabelClass='return node.attr.labelClass',
                      openOnClick=True,
                      #connect_onClick='genro.gotoURL($1.getAttr("file"),true)',
                      selected_file='frameset.selectedFile',
                      nodeId='_menutree_')
        leftPane.dataController("genro.wdgById('_gnrRoot').showHideRegion('left', false);", fired='^gnr.onStart',
                                appmenu="=gnr.appmenu", _if="appmenu.len()==0")
        leftPane.dataController("console.log(file);console.log(modifiers)", file="^frameset.selectedFile",
                                modifiers='=frameset.selectedFile?_modifiers')

    def getUserMenu(self):
        result = self.userMenu()
        while len(result) == 1:
            result = result['#0']
        return result

    def rootWidget(self, root, **kwargs):
        return root.stackContainer(_class='pbl_root', **kwargs)

    def main(self, rootSC, **kwargs):
        pane = rootSC.contentPane()
        indexurl = self.package.attributes.get('indexurl')
        indexurl = 'http://www.apple.com'
        frame = pane.iframe(height='100%', width='100%', border=0, src=indexurl, )