#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag,GeoCoderBag

class GnrCustomWebPage(object):
    maintable='devlang.developer'
    py_requires='public:Public,standard_tables:TableHandler,gnrcomponents/selectionhandler'
    
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('first_name', width='20em')
        r.fieldcell('last_name', width='20em')
        r.fieldcell('email', width='20em')
        r.fieldcell('@devlang_dev_lang_developer_id.@language_id.name',name='!!Languages',width='30em')
        return struct
        
    def formBase(self, parentBC,disabled=False, **kwargs):
        layout = parentBC.borderContainer(**kwargs)
        top = layout.contentPane(region='top',_class='pbl_roundedGroup',margin='10px')
        self.developer_form(top,disabled=disabled)
        center = layout.borderContainer(region='center',margin='10px',margin_top=0)
        self.developer_language_view(center)
    
    def developer_language_view(self,bc):
        iv = self.includedViewBox(bc,label='!!Languages',table='devlang.dev_lang',nodeId='dev_lang',
                                storepath='.@devlang_dev_lang_developer_id', 
                                struct=self.developer_language_struct,
                                autoWidth=True,add_action=True,del_action=True)
        gridEditor = iv.gridEditor()
        gridEditor.dbSelect(dbtable='devlang.language',value='^.language_id',
                            gridcell='@language_id.name',hasDownArrow=True)
        gridEditor.filteringSelect(gridcell='level',values='!!1:Low,2:Good,3:Great,4:Specialist,5:Guru')
        
    def developer_form(self,pane,disabled=None):
        pane.div('!!Developer',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=2, border_spacing='6px',width='600px',disabled=disabled)
        fb.field('first_name',autospan=1)
        fb.field('email',autospan=1)
        fb.field('last_name',autospan=1)
        fb.field('website',autospan=1)
        fb.div(colspan=2, height='1em')
        fb.field('address',validate_remote='geolocator',autospan=2)
        fb.field('country_code',autospan=1)
        fb.field('country_name',autospan=1)
        fb.field('area',autospan=1)
        fb.field('locality',autospan=1)
        fb.field('thoroughfare',autospan=1)
        fb.field('postal_code',autospan=1)
        fb.div('&nbsp;', colspan=2)
        pane.dataController("""
                        SET .country_code = geocodebag.getItem('CountryNameCode');
                        SET .country_name = geocodebag.getItem('CountryName');
                        SET .area = geocodebag.getItem('AdministrativeAreaName');
                        SET .subarea = geocodebag.getItem('SubAdministrativeAreaName');
                        SET .locality = geocodebag.getItem('LocalityName');
                        SET .thoroughfare = geocodebag.getItem('ThoroughfareName');
                        SET .postal_code = geocodebag.getItem('PostalCodeNumber');
                        SET .coordinates = geocodebag.getItem('coordinates');                                                    
                            """,geocodebag="^geocodebag")
        
    def rpc_geolocator(self,value,**kwargs):
        b = GeoCoderBag()
        result = Bag()
        b.setGeocode('geolocator',value)
        self.setInClientData('geocodebag',b['geolocator'])
        if b['geolocator.address']:
            result['value'] = b['geolocator.address']
        else:
            result['errorcode'] = '!!Wrong location'
        return result
        
    def developer_language_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@language_id.name', name='!!Language', width='20em',zoom=True)
        r.fieldcell('level',width='10em')
        return struct
        
######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Developer'
        
    def barTitle(self):
        return '!!Developer'
                  
    def orderBase(self):
        return 'last_name'
    
    def queryBase(self):
        return dict(column='last_name',op='contains', val='%')
        
    def tableWriteTags(self):
        return None
        
    def tableDeleteTags(self):
        return None