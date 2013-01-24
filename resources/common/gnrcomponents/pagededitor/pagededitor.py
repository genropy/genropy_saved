# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag


class PagedEditor(BaseComponent):
    css_requires='gnrcomponents/pagededitor/pagededitor'
    js_requires='gnrcomponents/pagededitor/pagededitor'

    @extract_kwargs(editor=True)
    @struct_method
    def pe_pagedEditor(self,pane,value=None,editor_kwargs=None,letterhead_id=None,**kwargs):
        frame = pane.framePane(_workspace=True,**kwargs)
        frame.dataController("""frame._pe_manager= new gnr.PagedEditorManager(frame);""",
                            frame=frame,_onStart=True)
        frame.dataRpc('dummy',self._pe_getLetterhead,letterhead_id=letterhead_id,_if='letterhead_id',
                        _onResult='kwargs._frame._pe_manager.letterheads=result;',_frame=frame)
        self._pe_editor(frame,value=value,**editor_kwargs)
        self._pe_preview(frame.right)
        return frame


    def _pe_editor(self,frame,value=None,**kwargs):
        pane = frame.center.contentPane()
        pane.ckeditor(value=value,childname='editor',**kwargs)
        pane.dataController("""
                                frame._pe_manager.onContentChanged(value);
                            """,value=value,frame=frame)

    def _pe_preview(self,pane):
        bar = pane.slotBar('zoombar,10,preview,0',closable=True,width='230px',preview_height='100%',splitter=True,border_left='1px solid silver')
        top = bar.zoombar.slotToolbar('5,zoomSlider,*',height='20px')
        pane.data('#WORKSPACE.zoom',.3)
        top.zoomSlider.horizontalSlider(value='^#WORKSPACE.zoom',minimum=0.3, maximum=1,
                                intermediateChanges=True, width='15em')

        bar.preview.div(height='100%').div(position='absolute',top='40px',left=0,right=0,bottom=0).div(position='absolute',top='0',left=0,right=0,bottom=0,zoom='^#WORKSPACE.zoom',overflow='auto',_class='pe_preview_box',pe_previewRoot=True)
        #box.div(_class='pe_pages',nodeId='pr_1')
        #box.div(_class='pe_pages')

    @public_method
    def _pe_getLetterhead(self,letterhead_id=None,**kwargs):
        letterheadtbl = self.db.table('adm.htmltemplate')
        next_letterhead_id = None
        if ',' in letterhead_id:
            letterhead_id,next_letterhead_id = letterhead_id.split(',')
        else:
            next_letterhead_id = letterheadtbl.readColumns(pkey=letterhead_id,columns='$next_letterhead_id') 
        result = Bag()
        base = letterheadtbl.getHtmlBuilder(letterhead_pkeys=letterhead_id)
        base.finalize(base.body)
        basehtml = base.root.getItem('#0.#1').toXml(omitRoot=True,autocreate=True,forcedTagAttr='tag',docHeader=' ',
                                        addBagTypeAttr=False, typeattrs=False, 
                                        self_closed_tags=['meta', 'br', 'img'])
        result.setItem('page_base',basehtml)
        if next_letterhead_id:
            next = letterheadtbl.getHtmlBuilder(letterhead_pkeys=next_letterhead_id)
            base.finalize(next.body)
            nexthtml = next.root.getItem('#0.#1').toXml(omitRoot=True,autocreate=True,forcedTagAttr='tag',docHeader=' ',
                                        addBagTypeAttr=False, typeattrs=False, 
                                        self_closed_tags=['meta', 'br', 'img'])
            result.setItem('page_next',nexthtml)
        return result


