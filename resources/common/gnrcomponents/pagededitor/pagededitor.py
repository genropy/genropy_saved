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
    #js_requires='gnrcomponents/pagededitor/pagededitor'

    @extract_kwargs(editor=True,tpl=dict(slice_prefix=False))
    @struct_method
    def pe_pagedEditor(self,pane,value=None,editor_kwargs=None,letterhead_id=None,pagedText=None,printAction=None,bodyStyle=None,
                        datasource=None,extra_bottom=None,tpl_kwargs=True,**kwargs):
        bodyStyle = bodyStyle or self.getPreference('print.bodyStyle',pkg='adm') or self.getService('print').printBodyStyle()
        frame = pane.framePane(_workspace=True,selfsubscribe_print='FIRE #WORKSPACE.print;',**kwargs)
        right = frame.right
        right.attributes.update(background='white')
        printId = 'pe_print_%s' %id(frame)
        frame.dataRpc('dummy',self.pe_printPages,
                    pages=pagedText.replace('^','='),
                    bodyStyle=bodyStyle,nodeId=printId,
                    _fired='^#WORKSPACE.print')
        if printAction is True:
            printAction = """genro.getFrameNode(this.getInheritedAttributes()['frameCode']).publish('print');"""
        center = frame.center.contentPane(overflow='hidden')
        editor = center.ckeditor(value=value,**editor_kwargs)
        bar = right.slotBar('0,previewPane,0',closable=True,width='270px',preview_height='100%',splitter=True,border_left='1px solid silver')
        bar.previewPane.pagedHtml(sourceText=value,pagedText=pagedText,letterheads='^#WORKSPACE.letterheads',editor=editor,letterhead_id=letterhead_id,
                                printAction=printAction,bodyStyle=bodyStyle,datasource=datasource,extra_bottom=extra_bottom,**tpl_kwargs)
        
        frame.dataRemote('#WORKSPACE.letterheads',self._pe_getLetterhead,letterhead_id=letterhead_id,_if='letterhead_id')#_userChanges=True)
        frame._editor = editor
        return frame


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


    @public_method
    def pe_printPages(self,pages=None,bodyStyle=None):
        self.getService('print').htmlToPdf(pages,self.site.getStaticPath('page:temp','pe_preview.pdf',autocreate=-1),pdf_margin_top='0mm',
                                                                                                  pdf_margin_bottom='0mm',
                                                                                                  pdf_margin_left='0mm',
                                                                                                  pdf_margin_right='0mm',
                                                                                                  bodyStyle=bodyStyle)
        self.setInClientData(path='gnr.clientprint',value=self.site.getStaticUrl('page:temp','pe_preview.pdf', nocache=True),fired=True)
