#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public,public:IncludedView'
    pageOptions = {'openMenu': False}

    def pageAuthTags(self, method=None, **kwargs):
        return None

    def windowTitle(self):
        return '!!Register explorer'

    def main(self, rootBC, **kwargs):
        tc = rootBC.rootTabContainer('!!Connections')
        self.dlg_cleanup(tc)
        #bottom['left'].button('refresh',fire='refresh_all')
        self.overview_pane(tc.borderContainer(title='!!Overview', datapath='overviewPane', design='sidebar'))
        self.user_pane(tc.borderContainer(title='!!Users', datapath='userPane'))
        self.connection_pane(tc.borderContainer(title='!!Connections', datapath='connectionPane'))
        self.page_pane(tc.borderContainer(title='!!Pages', datapath='pagesPane'))

        tc.css('.disconnected .dojoxGrid-cell', "color:red !important;")
        tc.css('.inactive .dojoxGrid-cell', "color:orange !important;")
        tc.css('.no_children .dojoxGrid-cell', "color:yellow !important;")
        tc.dataRpc('data', 'update_data', _onCalling="""genro.wdgById('user_grid').selectionKeeper('save');
                                                      genro.wdgById('connection_grid').selectionKeeper('save');
                                                      genro.wdgById('page_grid').selectionKeeper('save');
                                                      genro.wdgById('overview_user_grid').selectionKeeper('save');
                                                      genro.wdgById('overview_connection_grid').selectionKeeper('save');
                                                      genro.wdgById('overview_page_grid').selectionKeeper('save');

                                                                """, _onStart=True,
                   _timing=4, _fired='^refresh_all')
        tc.dataController("""
                        var result = new gnr.GnrBag();
                        connections.forEach(function(n){
                            if (current_user==n.attr['user']){
                                result.setItem(n.label,null,n.attr);
                            }
                        });
                        genro.wdgById('overview_connection_grid').selectionKeeper('save');
                        SET overview_data.user_connections = result;
                        """, current_user='^#overview_user_grid.selectedId', connections='=data.connections')
        tc.dataController("""
                        
                        var result = new gnr.GnrBag();
                        pages.forEach(function(n){
                            if (current_connection_id==n.attr['connection_id']){
                                result.setItem(n.label,null,n.attr);
                            }
                        });
                        genro.wdgById('overview_page_grid').selectionKeeper('save');
                        SET overview_data.connection_pages = result;
                        """,
                          current_connection_id='^#overview_connection_grid.selectedId', pages='=data.pages')

    def dlg_cleanup(self, pane):
        def cb_center(parentBC, **kwargs):
            pane = parentBC.contentPane(**kwargs)
            fb = pane.formbuilder(cols=1, border_spacing='3px')
            fb.numberTextbox(value='^.max_age', lbl='Max age')
            fb.checkbox(value='^.cascade', label='Cascade')

        dialog = self.simpleDialog(pane, datapath='cleanup_dialog', dlgId='dlg_cleanup',
                                   cb_center=cb_center, height='130px', width='300px', title='Cleanup')
        dialog.dataRpc('dummy', 'cleanup_register', _fired='^.save', register_type='=.opener',
                       _onResult='FIRE .close;FIRE refresh_all;', max_age='=.max_age', cascade='=.cascade')

    def rpc_cleanup_register(self, register_type=None, max_age=None, cascade=None):
        self.site.register.cleanup(max_age=max_age, cascade=cascade)


    def overview_pane(self, bc):
        self.overview_user_grid(bc.borderContainer(region='left', width='400px', splitter=True))
        self.overview_connection_grid(bc.borderContainer(region='top', height='50%', splitter=True))
        self.overview_page_grid(bc.borderContainer(region='center'))

    def overview_user_grid(self, bc):
        def struct(struct):
            r = struct.view().rows()
            r.cell('user', width='6em', name='User')
            r.cell('age', width='4em', dtype='L', name='Age')
            r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
            r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')
            return struct

        self.includedViewBox(bc,
                             nodeId='overview_user_grid',
                             tools_menu=self.toolsMenu(bc, 'overview_user_grid'),
                             datapath='.users',
                             storepath='data.users',
                             label='Current users',
                             struct=struct,
                             autoWidth=True, autoSelect=True)
        bc.dataController("FIRE #dlg_cleanup.open = 'users';", _fired="^.users.cleanup")

    def overview_connection_grid(self, bc):
        def struct(struct):
            r = struct.view().rows()
            r.cell('register_item_id', width='15em', name='Connection id')
            r.cell('user_ip', width='12em', name='User')
            r.cell('browser_name', width='10em', name='Browser')
            r.cell('age', width='4em', dtype='L', name='Age')
            r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
            r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')
            return struct

        self.includedViewBox(bc,
                             nodeId='overview_connection_grid',
                             tools_menu=self.toolsMenu(bc, 'overview_connection_grid'),
                             datapath='.connections',
                             storepath='overview_data.user_connections',
                             label='User connections',
                             struct=struct,
                             autoWidth=True, autoSelect=True)
        bc.dataController("FIRE #dlg_cleanup.open = 'connections';", _fired="^.connections.cleanup")

    def overview_page_grid(self, bc):
        def struct(struct):
            r = struct.view().rows()
            r.cell('register_item_id', width='15em', name='Page id')
            r.cell('connection_id', width='15em', name='Connection id')
            r.cell('user_ip', width='6em', name='User ip')
            r.cell('start_ts', width='11em', name='Start', dtype='DH')
            r.cell('pagename', width='10em', name='Pagename')
            r.cell('age', width='4em', dtype='L', name='Age')
            r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
            r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')
            return struct

        self.includedViewBox(bc,
                             nodeId='overview_page_grid',
                             tools_menu=self.toolsMenu(bc, 'overview_page_grid'),
                             datapath='.pages',
                             storepath='overview_data.connection_pages',
                             label='Connection pages',
                             struct=struct,
                             autoWidth=True, autoSelect=True)
        bc.dataController("FIRE #dlg_cleanup.open = 'pages';", _fired="^.pages.cleanup")

    def get_items(self, items, child_name=None, **kwargs):
        result = Bag()
        for key, item in items.items():
            _customClasses = []
            item['_pkey'] = key
            if item['last_refresh_age'] > 60:
                _customClasses.append('disconnected')
            elif item['last_event_age'] > 60:
                _customClasses.append('inactive')
            if child_name and not item[child_name]:
                _customClasses.append('no_children')
            item.pop('datachanges', None)
            result.setItem(key, None, _customClasses=' '.join(_customClasses), **item)
        return result

    def rpc_update_data(self, **kwargs):
        result = Bag()
        result['users'] = self.get_items(self.site.register.users(), 'connections')
        connections = self.site.register.connections()
        result['connections'] = self.get_items(connections, 'pages')
        pages = self.site.register.pages()
        result['pages'] = self.get_items(pages)
        return result

    def user_pane(self, bc):
        self.includedViewBox(bc,
                             nodeId='user_grid',
                             tools_menu=self.toolsMenu(bc, 'user_grid'),
                             datapath='.users',
                             storepath='data.users',
                             label='Current users',
                             struct=self._user_grid_struct,
                             autoWidth=True, autoSelect=True)
        bc.dataController("FIRE #dlg_cleanup.open = 'users';", _fired="^.users.cleanup")


    def _user_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('user', width='6em', name='User')
        r.cell('user_name', width='12em', name='Fullname')
        r.cell('user_tags', width='12em', name='Tags')
        r.cell('start_ts', width='11em', dtype='DH', name='Started')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')
        return struct

    def connection_pane(self, bc):
        self.includedViewBox(bc,
                             nodeId='connection_grid',
                             tools_menu=self.toolsMenu(bc, 'connection_grid'),
                             datapath='.connections', storepath='data.connections',
                             label='Current connections',
                             struct=self._connection_grid_struct,
                             autoWidth=True, autoSelect=True)
        bc.dataController("FIRE #dlg_cleanup.open = 'connections';", _fired="^.users.cleanup")

    def _connection_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Connection id')
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='12em', name='User')
        r.cell('browser_name', width='10em', name='Browser')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')
        return struct


    def page_pane(self, bc):
        self.includedViewBox(bc,
                             nodeId='page_grid',
                             tools_menu=self.toolsMenu(bc, 'page_grid'),
                             datapath='.pages', storepath='data.pages',
                             label='Current pages',
                             struct=self._page_grid_struct,
                             autoWidth=True, autoSelect=True)
        bc.dataController("FIRE #dlg_cleanup.open = 'pages';", _fired="^.pages.cleanup")


    def _page_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Page id')
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='6em', name='User ip')
        r.cell('connection_id', width='14em', name='Connection')
        r.cell('start_ts', width='11em', name='Start', dtype='DH')
        r.cell('pagename', width='8em', name='Pagename')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')
        return struct

    def toolsMenu(self, pane, gridId):
        tools_menu = Bag()
        tools_menu.setItem('cleanup', None, caption='Cleanup', action='FIRE .cleanup')
        tools_menu.setItem('send_message', None, caption='Send Message', action='FIRE .send_message')
        pane.data('#%s.tools_menu' % gridId, tools_menu)
        return '.tools_menu'