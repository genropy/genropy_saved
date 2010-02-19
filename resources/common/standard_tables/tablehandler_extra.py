#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import toText,splitAndStrip

import os

class FiltersHandler(BaseComponent):
    def filterBase(self):
        return
    def listToolbar_filters(self,pane):
        #trial
        pane.button('bbb')
        
    def th_filtermenu(self,queryfb):
        ddb = queryfb.dropDownButton('!!Set Filter',showLabel=False,iconClass='icnBaseAction',
                                        baseClass='st_filterButton')
        menu = ddb.menu(_class='smallmenu',action='FIRE list.filterCommand = $1.command')
        menu.menuline('!!Set new filter',command='new_filter')
        menu.menuline('!!Add to current filter',command='add_to_filter')
        menu.menuline('!!Remove filter',command='remove_filter')
        queryfb.dataController(""" var filter;
                                if (command=='new_filter'){
                                    filter = query.deepCopy();
                                }else if(command=='add_to_filter'){
                                    alert('add filter');
                                }else if(command=='remove_filter'){
                                    filter = null;
                                }
                                 genro.setData('_clientCtx.filter.'+pagename,filter);
                                 genro.saveContextCookie();
                            """,current_filter='=_clientCtx.filter.%s' %self.pagename,
                                query = '=list.query.where',
                                pagename=self.pagename,
                             command="^list.filterCommand")
        queryfb.dataController("if(current_filter){dojo.addClass(dojo.body(),'st_filterOn')}else{dojo.removeClass(dojo.body(),'st_filterOn')}",
                            current_filter='^_clientCtx.filter.%s' %self.pagename,_onStart=True)

class TagsHandler(BaseComponent):
    py_requires='foundation/tools:RemoteBuilder'
    def lst_tags_main(self,pane):
        self.managetags_dlg(pane)
        pane.button('Show tags',action='FIRE #recordtag_dlg.open')
        pane.button('Link tags',action="""FIRE #linktag_dlg.open;""")

        
    def form_tags_main(self,pane):
        self.linktag_dlg(pane)
        ph = pane.div(_class='button_placeholder',float='right')
        ph.button('!!Tags', float='right',action='FIRE #linktag_dlg.open;', 
                  iconClass="tb_button icnBaseAction",showLabel=False)#to change    
    
    def managetags_dlg(self,pane):
        def cb_bottom(parentBC,**kwargs):
            bottom = parentBC.contentPane(**kwargs)
            bottom.button('!!Close',baseClass='bottom_btn',float='right',margin='1px',fire='.hide')

        def cb_center(parentBC,**kwargs):
            bc = parentBC.borderContainer(**kwargs)
            self.selectionHandler(bc,label='!!Edit tags',
                                   datapath=".tags",nodeId='recordtag_view',
                                   table='%s.recordtag' %self.package.name,
                                   struct=self.recordtag_struct,hasToolbar=True,add_enable=True,
                                   del_enable=True,checkMainRecord=False,
                                   selectionPars=dict(where='$tablename =:tbl AND $maintag IS NULL',tbl=self.maintable,
                                                        order_by='tag'),
                                   dialogPars=dict(formCb=self.recordtag_form,height='180px',
                                                    width='300px',dlgId='_th_recortag_dlg',title='!!Record Tag',
                                                    default_tablename=self.maintable,lock_action=False))                                
        dialogBc = self.dialog_form(pane,title='!!Edit tag',loadsync=True,
                                datapath='gnr.recordtag',centerOn='_pageRoot',
                                height='250px',width='400px',
                                formId='recordtag',cb_center=cb_center,
                                cb_bottom=cb_bottom)
        dialogBc.dataController("FIRE #recordtag_view.reload;",nodeId="recordtag_loader")
        
    def recordtag_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tag',width='5em')
        r.fieldcell('description',width='10em')
        return struct

    def recordtag_form(self,parentContainer,disabled,table,**kwargs):
        bc = parentContainer.borderContainer(**kwargs)
        form = bc.contentPane(region='top',height='150px')
        fb = form.formbuilder(cols=1, border_spacing='4px',width='90%',dbtable=table)
        fb.field('tag',autospan=1)
        fb.field('description',autospan=1)
        fb.field('values',autospan=1,tag='simpleTextArea')
        
    def rpc_load_recordtag(self):
        #'%s.userobject' %self.package.name
        return self.db.table('%s.recordtag' %self.package.name).query(where='$tablename =:tbl',tbl=self.maintable).selection().output('grid')
        
    def rpc_save_recordtag(self,tags):
        tblrecordtag = self.db.table('%s.recordtag' %self.package.name)
        
        for r in tags.values():
            if not r['id']:
                r['tablename'] = self.maintable
                tblrecordtag.insertOrUpdate(r)
        self.db.commit()
        

    def linktag_dlg(self,pane):
        def cb_center(parentBC,**kwargs):
            pane = parentBC.contentPane(**kwargs)
            self.lazyContent('getFormTags',pane,pkeys='^.pkeys') 
                                                    
        dialogBc = self.dialog_form(pane,title='!!Link tag',loadsync=False,
                                datapath='form.linkedtags',allowNoChanges=False , 
                                height='300px',width='510px',centerOn='_pageRoot',
                                formId='linktag',cb_center=cb_center)                                
        dialogBc.dataController("""SET .data = new gnr.GnrBag({pkeys:pkeys}); 
                                   FIRE .loaded;""",
                                nodeId="linktag_loader",
                                pkeys="==genro.wdgById('maingrid').getSelectedPkeys();")
        dialogBc.dataRpc(".result",'saveRecordTagLinks',nodeId="linktag_saver",
                        data='=.data',_onResult='FIRE .saved;')
                        
    def rpc_saveRecordTagLinks(self,data=None):
        pkeys = data['pkeys']
        tagbag = data['tagbag']
        taglink_table = self.db.table('%s.recordtag_link' %self.package.name)
        for pkey in pkeys:
            self._assignTagOnRecord(pkey,tagbag,taglink_table)
        self.db.commit()
                        
    def _assignTagOnRecord(self,pkey,tagbag,taglink_table):
        print pkey
        for node in tagbag:
            tag = node.label
            value = [k for k,v in node.value.items() if v]
            print value
            if value:
                taglink_table.assignTagLink(self.maintable,pkey,tag,value[0])
                
                
    def remote_getFormTags(self,pane,pkeys=None,**kwargs):
        if len(pkeys)==1:
            tagbag = self.db.table('%s.recordtag_link' %self.package.name).getTagLinksBag(self.maintable,pkeys[0])
            pane.data('.tagbag',tagbag)
        table = self.db.table('%s.recordtag' %self.package.name)
        rows = table.query(where='$tablename =:tbl AND $maintag IS NULL',
                          tbl=self.maintable,order_by='$values desc,$tag').fetch()
        externalFrame = pane.div(_class='tag_frame bgcolor_medium',datapath='.tagbag',padding='10px')
        tag_table = externalFrame.div(style='display:table;width:100%')
        for j,r in enumerate(rows):
            values = r['values']
            tag = r['tag']
            description = r['description']
            buttons = []
            max_width=3
            if values:
                for val in values.split(','):
                    subtag,lbl = splitAndStrip('%s:%s'%(val,val),':',n=2,fixed=2)
                    buttons.append(dict(value='^.%s' %subtag,_class='dijitButtonNode tag_button tag_value',label=lbl))
                for b in buttons:
                    if len(b['label'])>max_width:
                        max_width = len(b['label'])
                max_width = '%fem' %(max_width*.7)
            else:
                buttons.append(dict(value='^.true',_class='dijitButtonNode tag_button tag_true',label='!!Yes'))
                
            oddOrEven = 'even'
            colorRow = 'bgcolor_bright'
            if j%2:
                oddOrEven = 'odd'
                colorRow = 'bgcolor_brightest'
            tag_row = tag_table.div(style='display:table-row',height='5px') #no dimensioni riga solo padding dimensioni ai contenuti delle celle
            tag_row = tag_table.div(style='display:table-row',_class='tag_line tag_%s' %(oddOrEven),datapath='.%s' %tag) #no dimensioni riga solo padding dimensioni ai contenuti delle celle
            label_col = tag_row.div(description,style='display:table-cell',_class='tag_label_col bgcolor_darkest color_brightest')
            tag_row.div(style='display:table-cell',_class=colorRow).div(_class='dijitButtonNode tag_button tag_false').radiobutton(value='^.false',label='!!No',group=tag)
            value_col = tag_row.div(style='display:table-cell',_class='tag_value_col %s' %colorRow)
            for btn in buttons:
                value_col.div(_class=btn['_class'],width=max_width).radiobutton(value=btn['value'],label=btn['label'],group=tag)
         
class StatsHandler(BaseComponent):
    def stats_main(self,parent,**kwargs):
        """docstring for stats_mainpane"""
        bc = parent.borderContainer(**kwargs)
        top = bc.contentPane(region='top',height='6ex',splitter=True)
        left = bc.contentPane(region='left',width='300px',datapath='.tree',splitter=True)
        center = bc.borderContainer(region='center')
        self.stats_top(top)
        self.stats_left(left)
        self.stats_center(center)
    
    def stats_top(self,pane):
        fb = pane.formbuilder(cols=2,border_spacing='4px')
        fb.filteringSelect(values=','.join(["%s:%s" %(k,v) for k,v in self.stats_modes_dict().items()]),
                            value='^.tree.tot_mode',lbl='!!Mode')
        #fb.button('Run',fire='.tree.totalize')
        
    def stats_left(self,pane):
        pane.tree(storepath='.root',inspect='shift',selectedPath='.currentTreePath',labelAttribute='caption',
                 selectedItem='#_grid_total.data',isTree=True,margin='10px',_fired='^.reload_tree',hideValues=True)
        pane.dataRpc('.root','stats_totalize',selectionName='=list.selectionName',
                        tot_mode='^.tot_mode',_if='tot_mode&&(selectedTab==1)',timeout=300000,
                        totalrecords='=list.rowcount',selectedTab='=list.selectedTab',
                        _onCalling="""genro.wdgById("_stats_load_dlg").show();
                                     SET #_grid_total.data = null;SET #_grid_detail.data = null;""",
                        _onResult='FIRE .reload_tree;genro.wdgById("_stats_load_dlg").hide();',
                        _fired='^.do_totalize')
        pane.dataController("""SET .root.data = null; FIRE .reload_tree; FIRE .do_totalize;""",_fired="^list.queryEnd")
        dlg = pane.dialog(nodeId='_stats_load_dlg',title='!!Loading')
        dlg.div(_class='pbl_roundedGroup',height='200px',width='300px').div(_class='waiting')
        
        
    def stats_center(self,bc):
        self.includedViewBox(bc.borderContainer(region='top',height='50%',splitter=True,margin='5px'),
                             label='!!Analyze Grid',datapath='.grids.total',nodeId='_grid_total',
                             storepath='.data',structpath='.struct',autoWidth=True,export_action=True)
        bc.dataRpc('#_grid_total.struct','stats_get_struct_total',tot_mode='^.tree.tot_mode')
        self.includedViewBox(bc.borderContainer(region='center',margin='5px'),
                            label=self._stats_detail_label,
                            datapath='.grids.detail',nodeId='_grid_detail',
                            storepath='.data',structpath='.struct',
                            table=self.maintable, autoWidth=True,export_action=True,
                            selectionPars=dict(method='stats_get_detail',
                                                flt_path='=stats.tree.currentTreePath',
                                                selectionName='=list.selectionName',
                                                _autoupdate='=.autoupdate',_if='_autoupdate',
                                                _else='null'))                     
        bc.dataRpc('#_grid_detail.struct','stats_get_struct_detail',tot_mode='^.tree.tot_mode')
    
    def _stats_detail_label(self,pane):
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        fb.div(self.pluralRecordName())
        fb.checkbox(value='^.autoupdate',label='!!Auto update',default=False,lbl=' ',lbl_width='1em')
        fb.dataController("FIRE .reload;",_fired="^stats.tree.currentTreePath",
                            autoupdate='^.autoupdate')

                        
    def rpc_stats_get_struct_total(self,tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct=self.stats_totals_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            if not 'dtype' in cellargs:
                if cellargs['field'].startswith('sum_') or cellargs['field'].startswith('avg_'):
                    cellargs['dtype'] = 'N' 
                elif cellargs['field'] == 'count' or cellargs['field'].startswith('count_'):
                    cellargs['dtype'] = 'L' 
            r.cell(**cellargs)
        return struct
    def rpc_stats_get_struct_detail(self,tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct=self.stats_detail_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            r.fieldcell(**cellargs)
        return struct
        
    def rpc_stats_get_detail(self, flt_path=None,selectionName=None, **kwargs):
        if not flt_path:
            return
        fieldpath = flt_path.split('.')[5:]
        fieldpath = '.'.join(fieldpath)
        selection = self.unfreezeSelection(self.tblobj, selectionName)
        result = selection.output('grid', subtotal_rows=fieldpath, recordResolver=False)
        return result

    def stats_modes_dict(self):
        """Override this"""
        return
        
    def stats_group_by(self,tot_mode=None):
        """Override this"""
        return
    def stats_sum_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_keep_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_collect_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_distinct_cols(self,tot_mode=None):
        """Override this"""
        return
        
    def stats_key_col(self,tot_mode=None):
        """Override this"""
        return

    def stats_tot_modes(self):
        """Override this"""
        return ''
    
    def stats_columns(self):
        """Override this"""
        return 
        
    def stats_get_selection(self,selectionName):
        if self.stats_columns():
            cust_selectionName = '%s_cust' %selectionName
            if not os.path.exists(self.pageLocalDocument(cust_selectionName)):
                return self.stats_create_custom_selection(selectionName,cust_selectionName)
            else:
                selectionName = cust_selectionName
        return self.unfreezeSelection(self.tblobj, selectionName)
        
    def stats_create_custom_selection(self,selectionName,cust_selectionName):
        pkeys = self.unfreezeSelection(self.tblobj, selectionName).output('pkeylist')
        query = self.tblobj.query(columns=self.stats_columns(),
                                    where='t0.%s in :pkeys' % self.tblobj.pkey,
                                    pkeys=pkeys,addPkeyColumn=False)
        return query.selection()
        
        
    def rpc_stats_totalize(self,selectionName=None,group_by=None,sum_cols=None,keep_cols=None,
                            collect_cols=None,distinct_cols=None,key_col=None,captionCb=None,
                            tot_mode=None,**kwargs):
        selection = self.stats_get_selection(selectionName)
        selection.totalize()
        
        group_by = group_by or self.stats_group_by(tot_mode)
        sum_cols = sum_cols or self.stats_sum_cols(tot_mode)
        keep_cols = keep_cols or self.stats_keep_cols(tot_mode)
        collect_cols = collect_cols or self.stats_collect_cols(tot_mode)
        distinct_cols = distinct_cols or self.stats_distinct_cols(tot_mode)
        key_col = key_col or self.stats_key_col(tot_mode)
        captionCb = captionCb or self.stats_captionCb(tot_mode)
        if isinstance(group_by,basestring):
            group_by = group_by.split(',')
        if isinstance(sum_cols,basestring):
            sum_cols = sum_cols.split(',')
        if isinstance(keep_cols,basestring):
            keep_cols = keep_cols.split(',')
        if isinstance(collect_cols,basestring):
            collect_cols = collect_cols.split(',')
        if isinstance(distinct_cols,basestring):
            distinct_cols = distinct_cols.split(',')
        def date_converter(mode):
            datefield,formatmode =mode.split(':')     
            return lambda r: toText(r[datefield],format=formatmode,locale=self.locale)
        for k,x in enumerate(group_by):
            if isinstance(x,basestring):
                if x.startswith('#DATE='):
                    group_by[k] = date_converter(x[6:])
                else:
                    group_by[k] = x.replace('@','_').replace('.','_')
        if keep_cols:
            keep_cols = [x.replace('@','_').replace('.','_') for x in keep_cols]
        if distinct_cols:
            distinct_cols = [x.replace('@','_').replace('.','_') for x in distinct_cols]
        result = Bag()
        data = selection.totalize(group_by=group_by,sum=sum_cols,keep=keep_cols,
                                    collect=collect_cols,distinct=distinct_cols,
                                    key=key_col,captionCb=captionCb)
        self.freezeSelection(selection,selectionName)
        result.setItem('data',data,caption=self.stats_modes_dict()[tot_mode])
        return result
        
    def stats_captionCb(self,tot_mode):
        def cb(group,row,bagnode):
            return bagnode.label
        return cb