#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrlist import getReader

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='100%')

    def th_order(self):
        return 'code'


class ConverterEditorView(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()    
        convertertbl = self.db.table('lgcy.converter')    
        for field in convertertbl.convertedFields():
            r.fieldcell(field,width='30em',
                        hidden='^main.lgcy_converter.view.sections.convertedtables.current?=#v!="conv_%s"' %field)
        r.fieldcell('code',width='20em')

    def th_order(self):
        return 'code'

    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@convertedtables')
        bar = top.bar.replaceSlots('addrow','addrow,importConversion,export,2')
        importer_structure = dict(mandatories='legacy')

        bar.importConversion.paletteImporter(paletteCode='importConverter',
                            #dockButton_iconClass=False,
                            dockButton_iconClass='iconbox inbox',
                            title='!!Import Converter Items',
                            importButton_label='Import',
                            previewLimit=50,
                            importButton_action="""
                                    genro.publish('import_converter_items',
                                                {filepath:imported_file_path,
                                                fkey:fkey.slice(5)})
                                """,
                            importButton_fkey='=main.lgcy_converter.view.sections.convertedtables.current',
                            #errorCb="""genro.dlg.alert('')""",
                            dropMessage='!!Drag your file or do double click here',
                            matchColumns='*',importerStructure=importer_structure)
        bar.dataRpc(None,self.importConverterItems,subscribe_import_converter_items=True,
                    _lockScreen=True,timeout=0)
    
    @public_method
    def importConverterItems(self,filepath=None,fkey=None):
        readerfile = self.site.storageNode(filepath)
        convertertbl = self.db.table('lgcy.converter')
        linkedtbl = convertertbl.column(fkey).relatedTable().dbtable
        with readerfile.local_path('rb') as local_path:
            reader = getReader(file_path=local_path)
        linkfield = reader.headers[0]
        linkdict = dict([(item[linkfield],item['legacy']) for item in reader() if item['legacy']])
        f = linkedtbl.query(where='$%s IN :linked' %linkfield,linked=linkdict.keys(),columns='$%s' %linkfield).fetch()
        for r in f:
            legacy_codes = linkdict[r[linkfield]].split(',')
            for lcode in legacy_codes:
                convertertbl.insert({fkey:r['pkey'],'code':lcode})
        self.db.commit()



    def th_sections_convertedtables(self):
        result = []
        convertertbl = self.db.table('lgcy.converter')    
        for field in convertertbl.convertedFields():
            result.append(dict(code='conv_%s' %field,caption=convertertbl.column(field).relatedTable().name_long,
                                condition="$%s IS NOT NULL" %field))
        return result
    


class ConverterEditorForm(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.div(margin_top='20px',margin_right='20px').formbuilder(cols=1, border_spacing='4px',width='100%')
        convertertbl = self.db.table('lgcy.converter')    
        for field in convertertbl.convertedFields():
            fb.field(field,width='100%',
                    validate_notnull='^main.lgcy_converter.view.sections.convertedtables.current?=#v=="conv_%s"' %field,
                    hidden='^main.lgcy_converter.view.sections.convertedtables.current?=#v!="conv_%s"' %field)
        fb.field('code',validate_notnull=True)



    def th_options(self):
        return dict(dialog_height='160px', dialog_width='400px')


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
