# -*- coding: UTF-8 -*-
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
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrbag import Bag
import datetime
from gnr.web.gnrwebstruct import struct_method

from gnr.core.gnrlocale import DATEKEYWORDS

class MenuStackContainer(BaseComponent):
    def menuStackContainer(self, parent, nodeId=None, selectedPage=None,
                           hasToolbar=False, label_cb=None, **kwargs):
        capId = '%s_caption' % nodeId
        menuId = '%s_menu' % nodeId
        bc = parent.borderContainer(**kwargs)
        top = bc.contentPane(region='top')
        if hasToolbar:
            top = top.toolbar(height='20px')
        else:
            top = top.div(_class='pbl_roundedGroupLabel')
        top.dataController("""
            var menuNode = genro.nodeById(menuId);
            menuNode.freeze();
            var stack= genro.wdgById(stackId);
            var children = stack.getChildren();
            var maxLength = 0;
            for (var i=0; i<children.length;i++){
                var attrs = children[i].sourceNode.attr;
                maxLength = maxLength<=attrs.title.length?attrs.title.length:maxLength;
                menuNode._('menuline',{label:attrs.title,idx:i});
                }
            menuNode.unfreeze();
            stack.setSelected(0);
            genro.dom.style(genro.domById(capId),{width:maxLength*.7+'em'});
            
        """, stackId=nodeId, _onStart=True, nodeId='%s_nav' % nodeId, menuId='%s_menu' % nodeId, capId=capId)
        navigator = top.div(_class='menuStackNavigator', float='left')
        navigator.button('!!Prev', iconClass='icnNavPrev', action='genro.wdgById("%s").back();' % nodeId,
                         showLabel=False, baseClass='no_background')
        navigator.dropDownButton(nodeId=capId, baseClass='no_background', padding_right='1.2em',
                                 text_align='center').menu(nodeId='%s_menu' % nodeId, _class='smallmenu',
                                                           action='genro.wdgById("%s").setSelected($1.idx);' % nodeId)
        navigator.button('!!Next', baseClass='no_background', iconClass='icnNavNext',
                         action='genro.wdgById("%s").forward();' % nodeId, showLabel=False)

        if label_cb:
            label_cb(top.div(float='left'))
        return bc.stackContainer(region='center', nodeId=nodeId, selectedPage=selectedPage,
                                 connect_addChild="""
                                                    var cb = function(){genro.wdgById('%s').setLabel($1.sourceNode.attr.title);};
                                                    dojo.connect(this.widget,'_showChild',cb);
                                                    """ % (capId))

class DynamicEditor(BaseComponent):
    css_requires = 'dyn_editor'

    def dynamicEditor(self, container, value, contentPars=None, disabled=None,
                      nodeId=None, editorHeight='', **kwargs):
        nodeId = nodeId or self.getUuid()
        stackId = "%s_stack" % nodeId
        editorId = "%s_editor" % nodeId
        st = container.stackContainer(nodeId=stackId, **contentPars)
        viewPane = st.contentPane(_class='pbl_viewBox')
        viewPane.div(innerHTML=value, _class='formattedBox')
        editPane = st.contentPane(overflow='hidden', connect_resize="""var editor = genro.wdgById('%s');
                                                   var height = this.widget.domNode.clientHeight-30+'px';
                                                   dojo.style(editor.iframe,{height:height});""" % editorId)
        editPane.editor(value=value, nodeId=editorId, **kwargs)
        st.dataController('genro.wdgById("%s").setSelected(disabled?0:1)' % stackId,
                          disabled=disabled, fired='^gnr.onStart')

class PeriodCombo(BaseComponent):
    css_requires = 'period_combo'

    def _pc_datesHints(self):
        today = datetime.date.today()
        dates = []
        dates.append(str(today.year))
        dates.append(str(today.year - 1))
        for k, v in DATEKEYWORDS[self.locale[:2]].items():
            if k != 'to':
                if isinstance(v, tuple):
                    v = v[0]
                dates.append(v)
        dates = ','.join(dates)
        return dates

    def periodCombo(self, fb, period_store=None, value=None, lbl='!!Period', dflt='',width=None,**kwargs):
        value = value or '^.period_input'
        period_store = period_store or '.period'
        fb.dataRpc('dummy', self.decodeDatePeriod, datestr=value,
                   _onResult="""if (result.getItem("valid")){
                                    var period = result.getItem("period");
                                    if(kwargs.datestr!=period){
                                        this.setRelativeData(this.attr.datestr,period,null,null,'puttingdefault');
                                    }
                                 }else{
                                    result.setItem('period_string','Invalid period');
                                 }
                                 var ds = objectPop(this,'_defaultset');
                                 if(ds){
                                    PUT %s = result;
                                 }else{
                                    SET %s = result;
                                 }
                                 """ %(period_store,period_store),_onBuilt=True,_defaultPeriod=dflt or False,
                    _onCalling="""if(_triggerpars.kw&&_triggerpars.kw.reason=="puttingdefault"){
                                        return false;
                                  };
                                  if(!datestr && _defaultPeriod){
                                      kwargs['datestr'] = _defaultPeriod;
                                      this._defaultset = true;
                                  }
                                  kwargs["datestr"]= kwargs["datestr"] || "";
                                  """)
        
        fb.combobox(lbl=lbl,value=value, width=width, tip='^%s.period_string' % period_store,
                    values=self._pc_datesHints(), margin_right='5px', padding_top='1px', **kwargs)

class SelectionBrowser(BaseComponent):
    def selectionBrowser(self, pane, rowcount, indexPath=None):
        pane.button('!!First', fire_first='.navbutton', iconClass="tb_button icnNavFirst",
                    disabled='^.atBegin', showLabel=False)
        pane.button('!!Previous', fire_prev='.navbutton', iconClass="tb_button icnNavPrev",
                    disabled='^.atBegin', showLabel=False)
        pane.button('!!Next', fire_next='.navbutton', iconClass="tb_button icnNavNext",
                    disabled='^.atEnd', showLabel=False)
        pane.button('!!Last', fire_last='.navbutton', iconClass="tb_button icnNavLast",
                    disabled='^.atEnd', showLabel=False)
        pane.dataController("""
                                var newidx;
                                var idx = this.getRelativeData(indexPath) || 0;
                                if (btn == 'first' || btn=='new'){newidx = 0;} 
                                else if (btn == 'last'){newidx = rowcount-1;}
                                else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                                else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                                this.setRelativeData(indexPath,newidx);
                                
                                """,
                            indexPath=indexPath, btn='^.navbutton',
                            rowcount=rowcount)

class RichTextEditor(BaseComponent):
    """This is the default toolbar definition used by the editor. It contains all editor features.
    Any of these options can be used in the toolbar= parameter. We pass a string parameter 
    to create a javascript array that is passed to the widget.
    
    To see more options, go to:
    http://docs.cksource.com/ckeditor_api/symbols/CKEDITOR.config.html#.stylesCombo_stylesSet
     config.toolbar_Full =
         [
          ['Source','-','Save','NewPage','Preview','-','Templates'],
          ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Print', 'SpellChecker', 'Scayt'],
          ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
          ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
          '/',
          ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
          ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
          ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
          ['Link','Unlink','Anchor'],
          ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak'],
          '/',
          ['Styles','Format','Font','FontSize'],
          ['TextColor','BGColor'],
          ['Maximize', 'ShowBlocks','-','About']
         ];
    """
    css_requires = 'rich_edit'
    js_requires = 'ckeditor/ckeditor'

    def RichTextEditor(self, pane, value, disabled=None, nodeId=None, toolbar=None, **kwargs):
        pane.attributes.update(overflow='hidden')
        editorId = None
        if nodeId:
            editorId = "%s_editor" % nodeId
        if isinstance(toolbar, basestring):
            tb = getattr(self, 'rte_toolbar_%s' % toolbar, None)
            toolbar = tb() if callable(tb) else tb
        return pane.ckeditor(value=value, nodeId=editorId, readOnly=disabled, toolbar=toolbar, **kwargs)

    def rte_toolbar_standard(self):
        return """[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink','-','Templates'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]"""

    def rte_toolbar_simple(self):
        return """[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-','Image','Table','HorizontalRule','PageBreak'],
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize','TextColor','BGColor']]"""


class FilterBox(BaseComponent):
    def _prepareFilterMenu(self, filterOn):
        colsMenu = Bag()
        fltList = splitAndStrip(filterOn, ',')
        for i,col in enumerate(fltList):
            caption = col
            if ':' in col:
                caption, col = col.split(':')
            colsMenu.setItem('r%i'%i, None,col=col, caption=caption, childcontent='')
        return colsMenu


    def filterBox(self, pane, datapath=None, nodeId=None, filterOn=None):
        """.filter
                field
                caption
                value
                current_value
                types
                """

        filterstore = datapath or '.filter'
        colsMenu = self._prepareFilterMenu(filterOn)
        searchbox = pane.div(datapath=filterstore, nodeId=nodeId)
        searchlbl = searchbox.div(float='left', margin_top='2px')
        searchlbl.data('.field', colsMenu['#0?col'])
        searchlbl.data('.caption', colsMenu['#0?caption'])
        searchlbl.data('.types', colsMenu)
        searchlbl.span(value='^.caption', _class='buttonIcon')
        searchlbl.menu(modifiers='*', _class='smallmenu', storepath='.types',
                       selected_col='.field',
                       selected_caption='.caption')

        searchbox.input(value='^.value', _class='searchInput searchWidth', font_size='1.0em',
                        connect_onkeyup="FIRE .current_value = $1.target.value;")

    def gridFilterBox(self, pane, gridId=None, datapath=None, filterOn=None, table=None, **kwargs):
        fltList = splitAndStrip(filterOn, ',')
        cols = []
        for col in fltList:
            caption = None
            if ':' in col:
                caption, col = col.split(':')
            if not caption:
                caption = self.db.table(table).column(col).name_long
            colList = splitAndStrip(col, '+')
            col = '+'.join([self.db.colToAs(c) for c in colList])
            cols.append('%s:%s' % (caption, col))
        self.filterBox(pane.div(float='right', margin_right='5px'), filterOn=','.join(cols),
                       datapath=datapath or '.filter', **kwargs)
        filtercontroller = pane.dataController(datapath=".filter")
        filtercontroller.dataController('genro.wdgById(gridId).applyFilter(value,null,field);',
                                        gridId=gridId, value="^.current_value", field='=.field')
        filtercontroller.dataController('genro.wdgById(gridId).applyFilter("",null,field);',
                                        gridId=gridId, field='^.field')
        
                       