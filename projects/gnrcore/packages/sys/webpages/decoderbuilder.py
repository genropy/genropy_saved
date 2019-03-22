#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='public:Public,gnrcomponents/formhandler:FormHandler,gnrcomponents/framegrid:FrameGrid'
    
    def windowTitle(self):
        return '!!Decoder builder'

    def main(self, root, **kwargs):

        callArgs = self.getCallArgs('decoder_folder')

        frame = root.rootBorderContainer(datapath='main',design='sidebar',title='!![it]Checklist viewer') 
        
        view = frame.frameGrid(frameCode='V_decoder_type',_class='noheader buttons_grid',
                            struct=self.struct_decoderType,region='left',
                            width='200px',datapath='.view',border='1px solid silver',
                            grid_autoSelect=True,
                            grid_multiSelect=False,
                            grid_sortedBy='descrizione',
                            margin='2px')
        bar = view.top.slotToolbar('2,vtitle,*,delrow,newtype,2')
        bar.vtitle.div('Decoder %(decoder_folder)s' %callArgs)
        bar.newtype.slotButton('New type',ask=dict(
                                    title='New',
                                    fields=[dict(name='name',lbl='Name',validate_notnull=True)]
                                ),action='genro.publish("newDecoderType",{name:name})')
        
        view.grid.fsStore(childname='store',folders='decoders:%(decoder_folder)s' %callArgs ,
                        _onStart=True,_fired='^main.types_reload')
        form = view.grid.linkedForm(frameCode='F_decoder_type',
                                 datapath='.form',loadEvent='onSelected',
                                 handlerType='border',childname='form',
                                 formRoot= frame.contentPane(region='center'),
                                 store='document')
        frame.dataRpc(None,self.newDecoderType,subscribe_newDecoderType=True,
                            decoder_folder=callArgs['decoder_folder'],
                            _onResult='FIRE main.types_reload')
        self.formDecoderType(form)

    def formDecoderType(self,form):

        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2)
        fb.textbox(value='^.name',lbl='!!Name')
        fb.button('Save',action='this.form.save();')


        left = bc.contentPane(region='left',width='300px').bagGrid(datapath='.record_types_grid',
                                                struct=self.record_types_struct,
                                                pbl_classes=True,title='Record Types',
                                                storepath='#FORM.record.record_types',
                                                grid_autoSelect=True,
                                                grid_multiSelect=False,
                                                grid_selected_code='#FORM.selectedRecordType')
        bar = left.top.bar.replaceSlots('addrow','new_rec_type')
        bar.new_rec_type.slotButton('New type',
                                    action="""
                                        if(!rtypes){
                                            rtypes = new gnr.GnrBag();
                                            SET #FORM.record.record_type = rtypes;
                                        }
                                        rtypes.setItem(code,new gnr.GnrBag({code:code,description:description}));
                                    """,
                                    rtypes='=#FORM.record.record_types',
                                    ask=dict(title='New',
                                                fields=[dict(name='code',lbl='Code',validate_notnull=True),
                                                        dict(name='description',lbl='Description')]
                                            )
                                    )
        bc.dataController("""
            SET #FORM.correntFieldTypesStore = code?this.absDatapath('#FORM.record.field_types.type_'+code):'temp';
        """,code='^#FORM.selectedRecordType')
        bc.contentPane(region='center').bagGrid(datapath='.field_types_grid',
                                                struct=self.field_types_struct,
                                                storepath='^#FORM.correntFieldTypesStore')

    def record_types_struct(self,struct):
        r=struct.view().rows()
        r.cell('code',name='Code',width='5em')
        r.cell('description',name='Description',edit=True,width='5em')


    def field_types_struct(self,struct):
        r=struct.view().rows()
        r.cell('position_start',name='S.Pos.',dtype='L',edit=True,width='5em')
        r.cell('position_end',name='E.Pos',dtype='L',edit=True,width='5em')
        r.cell('mandatory',name='Mand.',dtype='B',edit=True,width='5em')
        r.cell('datatype',name='Datatype',edit=dict(values='L:Int,N:Decimal,T:Text,D:Date'),width='10em')
        r.cell('name',name='Name',edit=True,width='20em')
        r.cell('validation',name='Validation',edit=dict(values='V,F,N,CONST'),width='10em')
        r.cell('constant_value',edit=True,width='10em',name='Const.')
        r.cell('description',name='Description',width='100%',edit=True)


    def struct_decoderType(self,struct):
        r=struct.view().rows()
        r.cell('name',name='Name',width='100%')

    @public_method
    def newDecoderType(self,name=None,decoder_folder=None,**kwargs):
        b = Bag(dict(name=name,record_types=Bag()))
        with self.site.storageNode('decoders:%s' %decoder_folder,'%s.xml' %name).open('wb') as f:
            b.toXml(f)