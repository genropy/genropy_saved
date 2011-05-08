#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" basecomponent """

from gnr.core.gnrbag import Bag
from gnr.web.gnrbaseclasses import BaseComponent


class Public(BaseComponent):
    css_requires = 'folder'

    def cancel_url(self):
        return "genro.gotoURL('index.py')"

    def publicPane(self, root, title=None, height=None, datapath=None, align=None, valign=None):
        """
        return top, client, bottom elements of a the public page layout of this package
        """
        lc, top = self._publicCommon(root, title=title, height=height)

        bottom = lc.contentPane(layoutAlign='bottom', _class='pbl_formContainerBottom')

        #lc.contentPane(layoutAlign='bottom', _class='pbl_formMsgBox').div('^_pbl.errorMessage')
        client = lc.contentPane(layoutAlign='client', _class='pbl_formContainerClient', datapath=datapath)
        if align or valign:
            client = client.table(width='100%', height='100%').tbody().tr().td(align=align or 'left',
                                                                               valign=valign or 'top')
        return (top, client, bottom)

    def publicPagedPane(self, root, title=None, height=None, selected='_pbl.selectedPage', **kwargs):
        """
        return a header and a stack container
        """
        lc, top = self._publicCommon(root, title=title, height=height)
        pages = lc.stackContainer(layoutAlign='client', _class='pbl_formContainerStack', selected='^%s' % selected,
                                  **kwargs)
        return (top, pages)

    def publicTabbedPane(self, root, title=None, height=None, **kwargs):
        """
        return a header and a tab container
        """
        lc, top = self._publicCommon(root, title=title, height=height)
        pages = lc.tabContainer(layoutAlign='client', _class='pbl_formContainerTab', **kwargs)
        return (top, pages)

    def publicPage(self, pages, datapath=None, align=None, valign=None, **kwargs):
        lc = pages.layoutContainer(**kwargs)

        bottom = lc.contentPane(layoutAlign='bottom', _class='pbl_formContainerBottom')
        #lc.contentPane(layoutAlign='bottom', _class='pbl_formMsgBox').div('^_pbl.errorMessage')
        client = lc.contentPane(layoutAlign='client', _class='pbl_formContainerClient', datapath=datapath)
        if align or valign:
            client = client.table(width='100%', height='100%').tbody().tr().td(align=align or 'left',
                                                                               valign=valign or 'top')
        return (client, bottom)

    def _publicCommon(self, root, title=None, height=None):
        lc = root.layoutContainer(_class='pbl_formContainer', height=height, gnrId='rootwidget')
        top = lc.contentPane(layoutAlign='top', _class='pbl_formContainerTitle')
        if title:
            top.div(title)
        return lc, top
