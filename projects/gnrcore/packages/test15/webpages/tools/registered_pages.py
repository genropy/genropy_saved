# -*- coding: UTF-8 -*-
# 
"""Registered pages tester"""
import datetime
from gnr.core.gnrbag import Bag, BagResolver

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme = 'claro'

    def test_1_registered_pages(self, pane):
        """On current page """
        box = pane.div(datapath='test1', height='500px', overflow='auto')
        box.button('Refresh', fire='.refresh_treestore')
        #box.dataRpc('.curr_pages.pages','curr_pages',
        #               _fired='^.refresh_treestore',_onResult='FIRE .refresh_tree')

        box.dataRemote('.curr_pages.pages', 'curr_pages', cacheTime=2)

        box.tree(storepath='.curr_pages', _fired='^.refresh_tree')


    def rpc_curr_pages(self):
        return PageListResolver()


class PageListResolver(BagResolver):
    classKwargs = {'cacheTime': 1,
                   'readOnly': False,
                   'pageId': None}
    classArgs = ['pageId']

    def load(self):
        if not self.pageId:
            return self.list_pages()
        else:
            return self.one_page()

    def one_page(self):
        register = self._page.site.register_page
        page = register.get_register_item(self.pageId)
        item = Bag()
        data = page.pop('data', None)
        item['info'] = Bag([('%s:%s' % (k, str(v).replace('.', '_')), v) for k, v in page.items()])
        item['data'] = data
        return item

    def list_pages(self):
        pagesDict = self._page.site.register_page.pages()
        result = Bag()
        for page_id, page in pagesDict.items():
            delta = (datetime.datetime.now() - page['start_ts']).seconds
            pagename = page['pagename'].replace('.py', '')
            user = page['user'] or 'Anonymous'
            ip = page['user_ip'].replace('.', '_')
            itemlabel = '%s (%s).%s (%i)' % (user, ip, pagename, delta)
            resolver = PageListResolver(page_id)
            result.setItem(itemlabel, resolver, cacheTime=1)
        return result 