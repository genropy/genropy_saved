.. _textmate:

========
Textmate
========
    
    *Last page update*: |today|
    
    Textmate is the Genro Team choice for text editor. You can download it from http://macromates.com/
    
    * :ref:`textmate_bundle`
        
        * :ref:`textmate_shortcuts`:
            
            * :ref:`shortcuts_web`:
            
                * :ref:`web_components`
                * :ref:`web_controllers`
                * :ref:`web_form`
                * :ref:`web_layout`
                * :ref:`web_handlers`
                
            * :ref:`shortcut_struct`
            * :ref:`shortcuts_sql`:
            
                * :ref:`sql_table`
                * :ref:`sql_trigger`
            
            * :ref:`shortcuts_validations`
            * :ref:`shortcuts_license`
            
.. _textmate_bundle:

Genro Bundle
============

    Download it from ...add???
    
.. _textmate_shortcuts:

Shortcuts
=========

    Here some general advices for shortcuts:
    
    * To use shortcuts, write the shortcut, then press the *Tab* key.
    * Many shortcuts will create some fields with two exclamation mark (``!!``) as begin string.
      The ``!!`` feature allows to create a multilanguage :ref:`project`. For more information,
      check the :ref:`languages` documentation page.
      
.. _shortcuts_web:
    
Web shortcuts
=============

.. _web_components:
    
components
----------

    * *inc*: write a :ref:`includedview` --> includedView(struct=,autoWidth=True,storepath='')
    * *iv*: write the :ref:`includedview`\box. You can choose between two options:
    
        * gnrweb: includedViewBox(dbselection)
        
        ::
    
            self.includedViewBox(bc,label='',datapath='',
                                 nodeId='',table='',autoWidth=True,
                                 struct=self.,columns='',hiddencolumns='',
                                 reloader='^', externalChanges='',
                                 selectionPars=dict(where='',='=')
                                 ,add_action=,del_action=)
                                 
        * gnrweb: includedViewBox(inline)
        
        ::
        
            iv = self.includedViewBox(bc,label='!!',
                                      storepath='', struct=,
                                      columns="""""",
                                      table='', autoWidth=True,
                                      add_action=True,del_action=True)
                                      
            gridEditor = iv.gridEditor()
                
.. _web_controllers:

controllers
-----------

    * *data*: write one of the :ref:`datacontroller_index`.
      You can choose between many options:
      
      * write a :ref:`dataformula` --> ``dataFormula("", "",_fired="")``
      * write a :ref:`datacontroller` --> ``dataController("",_fired="")``
      * write a :ref:`data` --> ``data("", "")``
      * write a :ref:`datascript` --> ``dataScript("dummy", "return;",_fired="")``
      * write a :ref:`datarecord` --> ``dataRecord('','',pkey='')``
      * write a :ref:`dataselection` --> ``dataSelection('','',where='')``
      * write a :ref:`datarpc` --> ``dataRpc('','',par='')``

.. _web_form:

form
----

    * *dbsel*: write a :ref:`dbselect` --> ``dbSelect(dbtable='',columns='',value='',_class='gnrfield')``
    * *fi*: write a :ref:`field` --> ``field('')``
    * *fc*: write a :ref:`fieldcell` --> ``fieldcell('',name='',width='')``
    * *fb*: write a :ref:`formbuilder` --> ``formbuilder(cols=, border_spacing='',disabled=disabled)``
    
      .. deprecated:: 0.7
        
                      please cancel the disabled attribute, that is deprecated.
    
.. _web_layout:
    
layout elements
---------------
    
    * *ac*: write a :ref:`accordioncontainer` --> ``accordionContainer()``
    * *bc*: write a :ref:`bordercontainer` --> ``borderContainer()``
    * *cp*: write a :ref:`contentpane` --> ``contentPane()``
    * *sc*: write a :ref:`stackcontainer` --> ``stackContainer()``
    * *tc*: write a :ref:`tabcontainer` --> ``tabContainer()``
    
.. _web_handlers:
    
handlers
--------

    * *on*: write an handler. You have many options:
    
        * page: handler onSaved
        
        ::
        
            def onSaved(self,record,resultAttr):
                pass
                
        * page: handler onSaving
        
        ::
        
            def onSaving(self, recordCluster, recordClusterAttr, resultAttr):
                pass
                
        * page: handler onLoading
        
        ::
        
            def onLoading(self,record,newrecord,loadingParameters,recInfo):
                pass
                

.. _shortcut_struct:

Struct shortcuts
================
    
    * *cel*: write row of a :ref:`struct` --> ``r.cell('', name='', width='')``
    * *str*: write a :ref:`struct`. You can choose between two options:
    
        * gnrweb: struct IV
        
            ::
        
                struct = self.newGridStruct()
                r = struct.view().rows()
                r.cell('', name='', width='')
            
        * gnrweb: struct IV (given struct)
        
            ::
            
                r = struct.view().rows()
                r.fieldcell('', name='', width='')
                
.. _shortcuts_sql:
    
SQL shortcuts
=============

.. _sql_table:

table elements
--------------
    
    * *col*: write a table :ref:`table_column`. You can choose between many options:
    
        * gnrsql: add column Text --> ``tbl.column('',name_long='!!')``
        * gnrsql: add column Char --> ``tbl.column('',size='',name_long='!!')``
        * gnrsql: add column varChar --> ``tbl.column('',size=':',name_long='!!')``
        * gnrsql: add column Int --> ``tbl.column('','L',name_long='!!')``
        * gnrsql: add column Decimal --> ``tbl.column('','N',name_long='!!')``
        * gnrsql: add column Real --> ``tbl.column('','R',name_long='!!')``
        * gnrsql: add column Date --> ``tbl.column('','D',name_long='!!')``
        * gnrsql: add column Xml --> ``tbl.column('','X',name_long='!!')``
          
          .. note:: use it also to instantiate a column with a :ref:`bag_intro` dtype
                
        * gnrsql: add column Bool --> ``tbl.column('','B',name_long='!!')``
        * gnrsql: add column Time --> ``tbl.column('','H',name_long='!!')``
        * gnrsql: add foreignkey --> ``tbl.column('',size='22',group='_',name_long='')``
        
    * *table*: write a :ref:`table`\'s header
    
            ::
            
                # encoding: utf-8
                
                class Table(object):
                    def config_db(self, pkg):
                        tbl =  pkg.table('',pkey='id',name_long='!!',
                                      name_plural='!!')
                        self.sysFields(tbl,id=False)
                        
    * *alias*: write an :ref:`table_aliascolumn` --> ``tbl.aliasColumn('',relation_path='',group='')``
    * *relation*: write a :ref:`table_relation` column attribute --> ``relation('',mode='foreignkey')``
    
.. _sql_trigger:

Triggers
--------
    
    * *trig*: write a :ref:`trigger`. You can choose between many options:
    
        * gnrsql: trigger(upd) --> ``def trigger_onUpdating(self, record_data, old_record):``
        * gnrsql: trigger(del) --> ``def trigger_onDeleting(self, record):``
        * gnrsql: trigger(ins) --> ``def trigger_onInserting(self, record_data):``
        
.. _shortcuts_validations:

Validations
===========

    * *val*: write a :ref:`validations`. You can choose between many options:
    
        * validate: notnull --> ``validate_notnull=True,validate_notnull_error='!!Required'``
        * validate: len --> ``validate_len='Too long:',validate_len_max='!!Too long',validate_len_min='!!Too long'``
        * validate: email --> ``validate_email=True, validate_email_error='!!Wrong email'``
        * validate: case --> ``validate_case=''``
        
.. _shortcuts_license:

GPL License
===========

    * *GPL*: write the GPL license::
    
        # This library is free software; you can redistribute it and/or
        # modify it under the terms of the GNU Lesser General Public
        # License as published by the Free Software Foundation; either
        # version 2.1 of the License, or (at your option) any later version.
        # 
        # This library is distributed in the hope that it will be useful,
        # but WITHOUT ANY WARRANTY; without even the implied warranty of
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
        # Lesser General Public License for more details.
        # 
        # You should have received a copy of the GNU Lesser General Public
        # License along with this library; if not, write to the Free Software
        # Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA