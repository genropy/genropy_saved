# -*- coding: utf-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from builtins import object
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
import os



class GnrCustomWebPage(object):
    py_requires='public:Public,gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler'
        
    def main(self,root,**kwargs):
        frame = root.rootContentPane(datapath='main',design='sidebar',title='!!Localization Manager')        
        frame.data('#FORM.enabledLanguages','en,it') 
        frame.data('#FORM.languages',Bag(self.db.application.localizer.languages))
        form = frame.center.frameForm(frameCode='localization',datapath='main',store='document')
        handler = form.store.handler('load',rpcmethod=self.loadLocalizationFile,
                                      currentLocalizationBlock='=#FORM.currentLocalizationBlock',
                                      enabledLanguages='=#FORM.enabledLanguages')
        form.dataController("""if(_triggerpars.kw.updvalue){
                this.form.reload();
            }
            """,enabledLanguages='^#FORM.enabledLanguages',_delay=4000)
        handler.addCallback("""SET #FORM.moduletree = result.popNode('treedata'); 
                                var struct = new gnr.GnrBag();
                                var r = new gnr.GnrBag();
                                struct.setItem('view_0.row_0',r);
                                r.setItem('cell_key',null,{field:'_lockey',width:'15em',name:'Key'});

                                r.setItem('cell_0',null,{field:'base',width:'23em',name:'Base'});
                                if(enabledLanguages){
                                    enabledLanguages.split(',').forEach(function(lang){
                                            r.setItem('cell_'+lang,null,{field:lang,width:'23em',name:languages.getItem(lang),edit:true});
                                        })
                                }
                                r.setItem('cell_path',null,{field:'path',width:'20em',name:'File',hidden:'^#FORM.filePathHidden',format_joiner:'<br/>'});
                                r.setItem('cell_ext',null,{field:'ext',width:'3em',name:'Ext'})
                                r.setItem('cell_pkey',null,{field:'_pkey',hidden:true})
                                SET #FORM.localizationGrid.grid.struct = struct;
                               return result""",enabledLanguages='=#FORM.enabledLanguages',languages='=#FORM.languages')
        form.store.handler('save',rpcmethod=self.saveLocalizationFile)
        self.localizerToolbar(form)
        bc = form.center.borderContainer()
        left = bc.contentPane(region='left',splitter=True,width='250px',overflow='auto').div(margin='10px')
        left.tree(storepath='#FORM.moduletree',_fired='^#FORM.controller.loaded',
                  hideValues=True,selectedLabelClass='selectedTreeNode',
                  selectedPath='#FORM.selectedTreePath',labelAttribute='caption')
        self.localizationGrid(bc.contentPane(region='center'))


    @public_method
    def loadLocalizationFile(self,path=None,currentLocalizationBlock=None,enabledLanguages=None,**kwargs):
        localizationpath = os.path.join(path,'localization.xml')
        localization = Bag(localizationpath) if os.path.exists(localizationpath) else Bag()
        localization.setBackRef()
        enabledLanguages = enabledLanguages.split(',') if enabledLanguages else []
        griddata = Bag()
        treedata = Bag()
        treedata.setItem('root',Bag(),caption=currentLocalizationBlock)
        treeroot = treedata['root']
        def cb(n):
            if n.attr.get('path'):
                treeroot.setItem(n.fullpath or n.label,None,path=n.attr['path'],ext=n.attr['ext'],caption=n.label)
            elif not n.value:
                row = griddata[n.label] 
                parentNode = n.parentNode
                parentAttr = parentNode.attr
                module = parentAttr.get('path')
                if not row:
                    row = Bag()
                    griddata[n.label] = row
                    row['base'] = n.attr.get('base')
                    row['ext'] = parentAttr.get('ext')
                    row['_lockey'] = n.label
                    row['path'] = []
                    row['_pkey'] = n.label
                row['path'].append(module)

                #row['_treepath'] = '%s.%s' %((parentNode.fullpath or parentNode.label),parentAttr.get('ext'))
                
                for lang in enabledLanguages:
                    row[lang] = row[lang] or n.attr.get(lang)
                
                
        localization.walk(cb)
        griddata.sort('base')
        return Bag(dict(content=Bag(griddata=griddata),treedata=treedata))

    @public_method
    def saveLocalizationFile(self,data=None,**kwargs):
        changesdict = dict()
        for k,v in list(data['griddata'].items()):
            filtered = v.filter(lambda n: '_loadedValue' in n.attr)
            if filtered:
                changesdict[v['_lockey']] = dict(filtered)
        localizer = self.db.application.localizer
        updatablebags = localizer.updatableLocBags['all' if self.isDeveloper() else 'unprotected']
        def cb(n,changedNodes=None,localizationDict=None):
            if n.label in changesdict:
                n.attr.update(changesdict[n.label])
                changedNodes.append(n.label)
                localizer_item =  localizationDict.get(n.label)
                if localizer_item:
                    localizer_item.update(changesdict[n.label])
        for destFolder in updatablebags:
            locbagpath = os.path.join(destFolder,'localization.xml')
            locbag = Bag(locbagpath) if os.path.exists(locbagpath) else Bag()
            changedNodes=[]
            locbag.walk(cb,changedNodes=changedNodes,localizationDict=localizer.localizationDict)
            if changedNodes:
                locbag.toXml(locbagpath)

    @public_method
    def rebuildLocalizationFiles(self,enabledLanguages=None,localizationBlock=None,do_autotranslate=None):
        localizer = self.db.application.localizer
        if localizer.translator and enabledLanguages and do_autotranslate:
            localizer.autoTranslate(enabledLanguages)
        self.db.application.localizer.updateLocalizationFiles(localizationBlock=localizationBlock)

    def localizerToolbar(self,form):
        items = Bag()
        for s in self.db.application.localizer.slots:
            items.setItem(s['code'],None,folderPath=s['destFolder'],code=s['code'])
        form.data('.blocks',items)

        bar = form.top.slotToolbar('2,mb,10,fblang,*,20,updateLoc,20,form_revert,form_save,form_semaphore,2')
        bar.mb.multiButton(value='^.currentLocalizationBlock',items='^.blocks',caption='code')
        languages = self.db.application.localizer.languages
        bar.fblang.formbuilder(cols=1,border_spacing='3px').checkboxText(value='^#FORM.enabledLanguages',values=','.join(["%s:%s" %(k,languages[k]) for k in sorted(languages.keys())]),popup=True,cols=4,lbl='!!Languages')
        bar.updateLoc.slotButton('Rebuild',do_autotranslate=False,
                                ask=dict(title='!![en]Options',
                                        fields=[dict(name='do_autotranslate',tag='checkbox',
                                                     label='!![en]Autotranslate')]),
                                action='FIRE #FORM.rebuildLocalization = do_autotranslate')
        bar.dataRpc('dummy',self.rebuildLocalizationFiles,do_autotranslate='^#FORM.rebuildLocalization',
                        enabledLanguages='=#FORM.enabledLanguages',
                    _onResult='this.form.reload()',localizationBlock='=.currentLocalizationBlock')
        form.dataController("""var attr = blocks.getAttr(currentLocalizationBlock);
                                this.form.goToRecord(attr.folderPath);""",
                                currentLocalizationBlock='^.currentLocalizationBlock',blocks='=.blocks',
                                _onStart=True)

    def localizationGrid(self,pane):
        frame = pane.bagGrid(storepath='=#FORM.record.griddata',datapath='#FORM.localizationGrid',pbl_classes=True,
                               margin='2px',struct=self.locGridStruct,
                                addrow=False,delrow=False,title='!!Localization',
                               grid_excludeListCb="""
                                   var result = [];
                                   var selectedModule= this.getRelativeData('#FORM.selectedModule');
                                   if (selectedModule){
                                       var store = this.store.getData();
                                       store.forEach(function(n){
                                           var v = n.getValue();
                                           var path = v.getItem('path').filter(k=>!isNullOrBlank(k));
                                           if(!path.some(function(p){                                                   
                                               return p.replace(/\//g, '.').startsWith(selectedModule)})){
                                               result.push(v.getItem('_pkey'))
                                           }
                                       },'static');
                                   }
                                   return result;
                                   """,
                                   grid_excludeCol='_pkey'
                                    )
        frame.dataController("""
            var selectedTreeNode = this.getRelativeData('#FORM.moduletree').getNode(selectedTreePath);
            var selectedModule = selectedTreePath.slice(5);
            if(selectedTreeNode && selectedTreeNode.attr.ext){
                 selectedModule +='.'+selectedTreeNode.attr.ext;
                 SET #FORM.filePathHidden = true;
            }else{
                SET #FORM.filePathHidden = false;
            }
            SET #FORM.selectedModule = selectedModule;
            SET .grid.struct?counter = genro.getCounter();

            grid.filterToRebuild(true);
            grid.updateRowCount('*');

            """,selectedTreePath='^#FORM.selectedTreePath',
                    grid=frame.grid.js_widget,_if='selectedTreePath')
        frame.top.bar.replaceSlots('#','2,vtitle,*,searchOn,2')



    def locGridStruct(self,struct):
        r = struct.view().rows()
        r.cell('_lockey',name='Key',width='23em')
        r.cell('base',name='Base',width='23em')
        r.cell('path',name='Filepath',width='20em',hidden='^#FORM.filePathHidden')
        r.cell('ext',name='Ext',width='3em')
        r.cell('_pkey',hidden=True)
