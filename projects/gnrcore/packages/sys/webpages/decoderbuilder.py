#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
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

        tc = form.center.tabContainer(margin='2px')
        self.typeDescriptor(tc.borderContainer(title='Descriptor'))
        self.typeTester(tc.borderContainer(title='Tester'))
    
    def typeTester(self,bc):
        top = bc.contentPane(region='top')
        fb = top.formbuilder()
        fb.dropUploader(label='Tester',uploadPath='page:decoder_tester',
                        onUploadingMethod=self.fileTestUploaded,
                        rpc_decoderpath= '=#FORM.pkey',
                        rpc_type_position='=#FORM.record.type_position',
                        onResult='genro.bp(true);')

        left = bc.contentPane(region='left',width='300px')
        left.tree(storepath='main.form.testerData')
        center = bc.contentPane(region='center')

    @public_method
    def fileTestUploaded(self,kwargs):
        filename = kwargs.get('filename')
        r = kwargs['file_handle'].file.read()
        type_position = kwargs['type_position'].split(',')
        type_position = [int(z) for z in type_position]
        with self.site.storageNode(kwargs['decoderpath']).open('rb') as f:
            decoder = Bag(f)
        parent_typecode = None
        result = Bag()
        field_types = decoder['field_types']
        dec = Bag()
        rowbag = Bag()
        i = 0
        for l in r.split('\r\n'):
            typecode = l[type_position[0]-1:type_position[1]]
            if typecode in field_types:
                parent_typecode = typecode
                dec = field_types[typecode]
                rowbag = Bag()
                result['r_%i' %i] = rowbag
                i+=1
            elif parent_typecode:
                dec = field_types['%s/%s' %(parent_typecode,typecode)]
            dec = dec or  Bag()
            for v in dec.values():
                if not v['name']:
                    continue
                rowbag['%s_%s' %(typecode,v['name'])] = l[v['position_start']-1:v['position_end']]
            #rowbag['type_%s' %typecode] = lb
        self.setInClientData('main.form.testerData',result)



    def typeDescriptor(self,bc):
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2)
        fb.textbox(value='^.name',lbl='!!Name')
        fb.textbox(value='^.type_position',lbl='!!Type position',width='4em')
        fb.button('Save',action='this.form.save();')
        center = bc.borderContainer(region='center')


        left = center.contentPane(region='top',height='300px',splitter=True).bagGrid(datapath='.record_types_grid',
                                                struct=self.record_types_struct,
                                                pbl_classes=True,title='Record Types',
                                                storepath='#FORM.record.record_types',
                                                grid_autoSelect=True,
                                                grid_multiSelect=False,
                                                grid_selfDragRows=True,
                                                grid_selected_code='#FORM.selectedRecordType')
        bar = left.top.bar.replaceSlots('addrow','new_rec_type')
        bar.new_rec_type.slotButton('New type',
                                    action="""
                                        if(!rtypes){
                                            rtypes = new gnr.GnrBag();
                                            SET #FORM.record.record_type = rtypes;
                                        }
                                        var currval = this.getRelativeData(correntFieldTypesStore) || new gnr.GnrBag();
                                        rtypes.setItem(code.replace('.','/'),
                                                        new gnr.GnrBag({code:code,description:description}));
                                        this.setRelativeData(this.absDatapath('#FORM.record.field_types.'+code.replace('.','/')),
                                                                                currval.deepCopy());
                                    
                                    """,
                                    rtypes='=#FORM.record.record_types',
                                    correntFieldTypesStore='=#FORM.correntFieldTypesStore',
                                    ask=dict(title='New',
                                                fields=[dict(name='code',lbl='Code',validate_notnull=True),
                                                        dict(name='description',lbl='Description')]
                                            )
                                    )
        bc.dataController("""
            SET #FORM.correntFieldTypesStore = code?this.absDatapath('#FORM.record.field_types.'+code.replace('.','/')):'temp';
        """,code='^#FORM.selectedRecordType')
        center.contentPane(region='center').bagGrid(datapath='.field_types_grid',
                                                struct=self.field_types_struct,
                                                storepath='^#FORM.correntFieldTypesStore')

    def record_types_struct(self,struct):
        r=struct.view().rows()
        r.cell('code',name='Code',width='5em')
        r.cell('description',name='Description',edit=True,width='15em')
        r.cell('notes',name='Notes',edit=True,width='100%')


    def field_types_struct(self,struct):
        r=struct.view().rows()
        r.cell('position_start',name='S.Pos.',dtype='L',edit=True,width='5em')
        r.cell('position_end',name='E.Pos',dtype='L',edit=True,width='5em')
        r.cell('name',name='Name',edit=True,width='20em')
        r.cell('iskey',name='Key',dtype='B',edit=True,width='5em')
        r.cell('mandatory',name='Mand.',dtype='B',edit=True,width='5em')
        r.cell('datatype',name='Datatype',edit=dict(values='L:Int,N:Decimal,T:Text,D:Date'),width='10em')
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