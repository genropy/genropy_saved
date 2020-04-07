# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA



"""
Component for menu handling:
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver
from gnr.core.gnrdecorator import public_method

class MenuIframes(BaseComponent):
    css_requires='frameplugin_menu/frameplugin_menu'

    def mainLeft_iframemenu_plugin(self, tc):
        frame = tc.framePane(title="Menu", pageName='menu_plugin')
        frame.top.slotToolbar('2,searchOn,*',searchOn=True)
        if not self.isMobile:
            frame.bottom.slotToolbar('5,newWindow,*')
        bc = frame.center.borderContainer()
        tbl = bc.contentPane(region='bottom').div(height='40px',margin='5px',_class='clientlogo')
        self.menu_iframemenuPane(bc.contentPane(region='center').div(position='absolute', top='2px', left='0', right='2px', bottom='2px', overflow='auto'))

    def btn_iframemenu_plugin(self,pane,**kwargs):
        pane.pluginButton('iframemenu_plugin',caption='!!Menu',
                            iconClass='iframemenu_plugin_icon',defaultWidth='210px')


                 
    def menu_iframemenuPane(self, pane, **kwargs):
        b = Bag()
        root_id = None
        customMenu = self.db.table('adm.menu').getMenuBag(root_id=root_id,userTags=self.userTags)
        if customMenu:
            b['root'] = customMenu 
        else:
            b['root'] = MenuResolver(path=getattr(self,'menu_path',None), pagepath=self.pagepath,_page=self)
            #b.getIndex()
        pane.data('gnr.appmenu', b)
        #leftPane = parentBC.contentPane(width='20%',_class='menupane',**kwargs)
        menutree = pane.tree(id="_gnr_main_menu_tree", storepath='gnr.appmenu.root', selected_file='gnr.filepath',
                  labelAttribute='label',
                  hideValues=True,
                  _class='menutree',
                  persist='site',
                  inspect='AltShift',
                  identifier='#p',
                  getIconClass="""function(item,opened){
                        if(!item.attr.isDir){
                            return "treeNoIcon";
                        }
                        return opened? 'opendir':'closedir';                        
                    }""",
                  getLabelClass="return node.attr.labelClass;",
                  openOnClick=True,
                  connect_onClick="""this.publish('selectMenuItem',{fullpath:$1.getFullpath(null,true),
                                                                    relpath:$1.getFullpath(null,genro.getData(this.attr.storepath)),
                                                                  modifiers:$2.__eventmodifier});""",
                  autoCollapse=True,
                  selfsubscribe_selectMenuItem="""
                        var node = genro.getDataNode($1.fullpath);
                        var labelClass= node.attr.labelClass;
                        var inattr = node.getInheritedAttributes();    
                        var selectingPageKw = objectUpdate({name:node.label,pkg_menu:inattr.pkg_menu,"file":null,table:null,
                                                            formResource:null,viewResource:null,fullpath:$1.fullpath,
                                                            modifiers:$1.modifiers},node.attr);
                        if(genro.isMobile){
                            genro.publish('setIndexLeftStatus',false);
                        }
                        if (genro.isMobile && false){
                            genro.framedIndexManager.makePageUrl(selectingPageKw);
                            genro.openWindow(selectingPageKw.url,selectingPageKw.label);
                        }
                        else if (selectingPageKw.externalWindow==true || selectingPageKw.modifiers == 'Shift'){
                            genro.publish("newBrowserWindowPage",selectingPageKw);
                        }else{
                            if(labelClass.indexOf('menu_existing_page')<0){
                                node.setAttribute('labelClass',labelClass+' menu_existing_page');
                            }   
                            this.publish("selected",selectingPageKw);
                        }    
                        if($1.doSelect){
                            this.widget.setSelectedPath(null,{value:node.getFullpath(null,genro.getData(this.attr.storepath))});
                        }
                  """,
                  nodeId='_menutree_')
   
        pane.dataRpc('dummy',self.menu_refreshAppMenu,
                    _onResult="""
                        genro.getDataNode('gnr.appmenu.root').refresh(true);
                        if(kwargs.selectPath){
                            kwargs._menutree.publish('selectMenuItem',{fullpath:kwargs.selectPath,doSelect:true}); 
                        }
                    """,subscribe_refreshApplicationMenu=True,_menutree=menutree)

    @public_method
    def menu_refreshAppMenu(self,**kwargs):
        self.application.clearSiteMenu()




class MenuResolver(BagResolver):
    classKwargs = {'cacheTime': 300,
                   'readOnly': False,
                   'path': None,
                   'pagepath': None,
                   '_page':None}
    classArgs = ['path']


    def resolverSerialize(self):
        attr = super(MenuResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

    def load(self):
        sitemenu = self._page.userMenu or self._page.application.siteMenu
        userTags = self._page.userTags
        dbstore = self._page.dbstore

        result = Bag()
        level = 0
        if self.path:
            level = len(self.path.split('.'))
        for node in sitemenu[self.path]:
            allowed = True
            nodeattr = node.attr
            externalSite = node.attr.get('externalSite')
            if externalSite:
                externalSite = self._page.site.config['externalSites'].getAttr(externalSite)['url']
            nodetags = nodeattr.get('tags')
            filepath = nodeattr.get('file')
            checkenv = nodeattr.get('checkenv')
            multidb = nodeattr.get('multidb')            
            dashboard = nodeattr.get('dashboard')
            if nodeattr.get('dashboard'):
                dashboards = self._getDashboards(pkg=nodeattr['dashboard'])
                if not dashboards:
                    continue
                node.value = dashboards
            if (multidb=='slave' and not dbstore) or (multidb=='master' and dbstore):
                allowed = False
            aux_instance = nodeattr.get('aux_instance')
            if nodetags:
                allowed = allowed and self._page.application.checkResourcePermission(nodetags, userTags)
            allowed = allowed and self._page.application.allowedByPreference(**nodeattr)
            if not aux_instance:
                tableattr = self._page.db.table(nodeattr['table']).attributes if 'table' in nodeattr else None
                if tableattr:
                    allowed = allowed and self._page.application.allowedByPreference(**tableattr)
            if allowed and filepath:
                allowed = self._page.checkPermission(filepath)
            if checkenv:
                allowed = allowed and self._page.rootenv[checkenv]
            if allowed:
                value=node.getValue()
                if node.resolver:
                    basepath='%(pkg)s/%(dir)s' % node.attr if 'dir' in node.attr else node.attr.get('basepath')
                    def cb(n):
                        n.attr['aux_instance'] = n.attr.get('aux_instance') or aux_instance
                        n.attr['label']=n.attr.get('caption')
                        if n.attr.get('file_ext')== 'py':
                            n.attr['file']= '%s/%s' %(basepath,n.attr.get('rel_path'))
                        else:
                            n.attr['basepath']=basepath
                            n.attr['child_count']=len(n.value)
                    value.walk(cb)
                attributes = {}
                attributes.update(node.getAttr())
                labelClass = 'menu_level_%i' % level
           
                if isinstance(value, Bag):
                    attributes['isDir'] = True
                    newpath = '%s.%s' % (self.path, node.label) if self.path else node.label
                    value = MenuResolver(path=newpath, pagepath=self.pagepath,_page=self._page)()
                   # labelClass = 'menu_level_%i' % level
                else:
                    value = None
                    labelClass = '%s menu_page' %labelClass
                    if 'file' in attributes and  attributes['file'].endswith(self.pagepath.replace('.py', '')):
                        labelClass = 'menu_page menu_current_page'
                    if 'workInProgress' in attributes:
                        labelClass+=' workInProgress'
                customLabelClass = attributes.get('customLabelClass', '')
                attributes['externalSite'] = externalSite
                attributes['labelClass'] = 'menu_shape %s %s' % (labelClass, customLabelClass)
                result.setItem(node.label, value, attributes)
        return result

    def _getDashboards(self,pkg=None):
        if not self._page.db.package('biz'):
            return
        result = Bag()
        f = self._page.db.table('biz.dashboard').query(where='$pkgid=:pk' if pkg is not True else None).fetch()
        for i,r in enumerate(f):
            if r['private']:
                continue
            label = 'dash_%s' %i
            result.setItem(label,None,file='/biz/dashboards/%(pkgid)s/%(code)s' %r,label=r['description'] or r['code'])
        return result