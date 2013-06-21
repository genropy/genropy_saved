#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  index.py
#
#

""" index.py """

import os 
from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url='genropynet.html'
    auth_workdate = 'admin'
    plugin_list = 'iframemenu_plugin,chat_plugin'
    css_requires='customstyles'

    def windowTitleTemplate(self):
        return "GenroPy Developer $workdate" 

    def windowTitle(self):
        return 'Genropy'

    def isDeveloper(self):
        return True

    def onUserSelected(self,avatar,data):
        if 'demo' in avatar.user_tags:
            data['custom_index'] = 'demo'

    def index_demo(self,root,**kwargs):
        frame = root.framePane()
        sc = frame.center.stackContainer()
        sc.contentPane().div('Tutorial')
        sc.contentPane(overflow='hidden',_lazyBuild=True).iframe(height='100%', width='100%', border=0, src='^iframe.selected_page')
        sc.dataController("sc.switchPage(page?1:0);",page='^iframe.selected_page',sc = sc.js_widget)
        self.left_menu(frame.left)
        #self.demoTop(frame.top)
        self.prepareBottom(frame.bottom)

    def demoTop(self,top):
        bar = top.slotBar('*,demotitle,*',background='#3E454C',color='white')
        bar.demotitle.div('Genropy Demo Tutorial',font_size='22px')
        
    def left_menu(self, pane):
        pane.data('menubag', self.diskDirectory())
        bar = pane.slotBar('2,datatree,2',width='200px',splitter=True,closable='open')
        datatreeslot = bar.datatree
        datatreeslot.attributes.update(height='100%',position='relative')
        treebox = datatreeslot.div(position='absolute',top='0',right='0',bottom='0',
                                left='0',overflow='auto',text_align='left',padding='5px',gradient_from='#efefef',gradient_to='#ffffff',gradient_deg=-90,_lazyBuild=True)

        treebox.tree(storepath='menubag', hideValues=True, inspect='shift', labelAttribute='name',
                  isTree=False, selected_path='tree.current_path', selected_name='tree.name',openOnClick=True,
                  selectedLabelClass='selectedTreeNode',_class="fieldsTree noIcon",
                        getLabelClass="""function(item){
                                            var _class = [];
                                            if(item._value){
                                                _class.push('fieldsTree_folder');
                                            }
                                            return _class.join(' ');}""",font_size='13px',color='#666',line_height='16px')
        treebox.dataController("""if (current_path){SET iframe.selected_page=current_path;}""",
                               current_path="^tree.current_path")
                               

        
####### server side operation #######
    
    def diskDirectory(self):
        pages = Bag(self.site.sitemap['gnrtutor'])['tutorial']
        for k in pages.keys():
            if hasattr(pages[k], '_htraverse'):
                pages[k].sort()
        return pages
        
    @public_method
    def fileSysPath(self, relpath=None):
        if not relpath:
            return ''
        basedir = __file__.strip('/').split('/')[:-1]
        basedir = u'/' + '/'.join(basedir)
        sys_path = os.path.join(basedir, relpath)
        return sys_path
        
   
        
    @public_method
    def demoCurrentName(self, relpath=None):
        name = relpath.split('/')[-1]
        return name