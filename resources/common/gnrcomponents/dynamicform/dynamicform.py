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
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwebstruct import struct_method

class DynamicForm(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGrid'
    
    @struct_method
    def df_fieldsGrid(self,pane,storepath=None,standard_range=False,title=None,**kwargs):   
        def struct(struct):
            r = struct.view().rows()
            r.cell('code', name='!!Code', width='5em')
            r.cell('description', name='!!Description', width='15em')
            r.cell('field_type', name='!!Type', width='10em')
        
            r.cell('field_source', name='!!Source', width='10em')
            r.cell('range', name='!!Min:Max',width='10em')
            #r.cell('max', name='!!Max',dtype='N', width='5em')
            if standard_range:
                r.cell('standard_range', name='Std.Range', width='10em')
            r.cell('formula', name='!!Formula', width='10em')  
            r.checkboxcell('do_summary', name='!!Summary',width='6em')       
            r.checkboxcell('mandatory', name='!!Mandatory',width='7em')  
            
        frame = pane.frameGrid(storepath=storepath,struct=struct,datamode='bag',datapath='#FORM.fieldsGrid_%i' %id(pane),**kwargs)
        ge = frame.grid.gridEditor()
        ge.textbox(gridcell='code')
        ge.textbox(gridcell='description')
        ge.filteringSelect(gridcell='field_type',values='!!T:Text,TL:Long Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time')
        ge.textbox(gridcell='field_source')
        ge.textbox(gridcell='range')
        if standard_range:      
            ge.textbox(gridcell='standard_range')
        ge.textbox(gridcell='formula')
        frame.top.slotToolbar('3,gridtitle,*,delrow,addrow,2',gridtitle=title or '!!Fields',delrow_parentForm=True,addrow_parentForm=True)
        return frame 
    @struct_method
    def df_dynamicFieldsPane(self,pane,df_table=None,df_pkey=None,df_folders=None,**kwargs):
        pane.remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,
                    df_folders=df_folders,
                    **kwargs)

    
    @public_method
    def df_remoteDynamicForm(self,pane,df_table=None,df_pkey=None,df_folders=None,datapath=None,**kwargs):
        if not df_pkey:
            pane.div('!!No Form descriptor')
            return
        fb_kwargs = dictExtract(kwargs,'fb_',pop=True)
        dbstore_kwargs = dictExtract(kwargs,'dbstore_',pop=True)
        pane.attributes.update(kwargs)
        df_tblobj = self.db.table(df_table)
        formDescriptor = df_tblobj.getFormDescriptor(pkey=df_pkey,folders=df_folders)
        fields = formDescriptor[df_tblobj.attributes.get('df_fields','fields')]
        fb_kwargs.setdefault('datapath',datapath)
        fielddict = {'T':'Textbox','L':'NumberTextBox','D':'DateTextBox','B':'Checkbox','N':'NumberTextBox', 'TL':'Simpletextarea'}
        fb = pane.formbuilder(**fb_kwargs)
        for fnode in fields:
            attr = fnode.attr
            field_type = attr.pop('field_type')
            tag = fielddict[field_type]
            colspan = 2 if tag == 'Simpletextarea' else 1
            field_source = attr.pop('field_source',None)
            if field_source:
                if '.' in field_source:
                    tag = 'dbSelect'
                    attr['dbtable'] = field_source
                    pkg,tblname = field_source.split('.')
                    if pkg in dbstore_kwargs.get('pkg','').split(','):
                        attr['_storename'] = '=%(name)s' %dbstore_kwargs
                else:
                    if ':' in field_source:
                        tag = 'FilteringSelect'
                    else:
                        tag = 'ComboBox'
                    attr['values'] = field_source
            fb.child(value='^.%(code)s' %attr, lbl='%(description)s' %attr,colspan=colspan,tag=tag,**attr)
        

 #  @public_method
 #  def df_remoteDynamicForm(self,pane):
 #      fields,stampabile,descrizione = self.db.table(cfg_table).getFields(code=code)
 #      if not fields:
 #          return
 #      stampa=False
 #      n_colonne = 1
 #      
 #      lista_check = []
 #      # if len(fields)>1:
 #      #     helper = fields[1]
 #      #     # nome_tab = helper.get('nome_tab')
 #      #     n_colonne = helper.get('n_colonne') or 1      
 #      #     stampa = helper.get('stampa', False)  
 #      #     kwargs['fld_margin_right'] = '50px'
 #      #     fields = fields[0]
 #          
 #      
 #      fb = pane.formbuilder(cols=n_colonne, border_spacing='2px',lbl_width='100%',fld_width="22em",datapath=path_databag,**kwargs)
 #      fielddict = {'T':'Textbox','L':'NumberTextBox','D':'DateTextBox','B':'Checkbox','N':'NumberTextBox', 'TL':'Simpletextarea'}
 #      tpl = []
 #      grafico = False
 #      for n in fields:
 #          attr = n.attr
 #          fld = None
 #          values=attr.get('values')
 #          obbligatorio = attr.get('obbligatorio') == 'Si'
 #          kwargs = dict(value='^.%s' %attr['codice'],lbl=attr['descrizione'],margin_top="2px", required=obbligatorio, validate_notnull=obbligatorio)
 #          
 #          if values:
 #              if values.startswith('*'):
 #                  tag = 'dbselect'
 #                  table = values[1:]
 #                  kwargs['dbtable'] = table
 #                  kwargs['selectedCaption'] = '.%s_d' %attr['codice']
 #              else:
 #                  tag = 'filteringSelect'
 #                  p = re.compile(', ')
 #                  values = p.sub(',',values)
 #                  kwargs['values'] = values
 #                  kwargs['selectedCaption'] = '.%s_d' %attr['codice']
 #          else:
 #              if attr.get('tipo_campo') != 'GR':
 #                  tag = fielddict[attr.get('tipo_campo') or 'T']
 #              
 #          if tag == 'Simpletextarea':
 #              kwargs['style']="width:100%;resize:both !important;" #FIX LARGHEZZA TEXTAREA
 #              kwargs['rows']=3
 #              kwargs['lblvalign']='top'
 #              
 #          kwargs['tag'] = tag
 #             
 #          if attr.get('minimo') is not None:
 #              kwargs['validate_min'] = attr['minimo']
 #          if attr.get('massimo') is not None:
 #              kwargs['validate_max'] = attr['massimo']
 #          formula = attr.pop('formula',None)
 #          pane.data('$formula', formula)
 #          if formula and attr.get('tipo_campo') != 'GR':
 #              kwargs['readOnly'] = True
 #              kwargs['lbl_style'] ="text-transform:uppercase;font-weight:bold;"
 #              if formula == "=TOT":
 #                  formulaTot=""
 #                  formulaArgs = dict([(str(x),'^.%s' %x) for x in fields.digest('#a.codice') if x!=attr['codice']])
 #                  for x in fields.digest('#a.codice'):
 #                      if x!=attr['codice']:
 #                          formulaTot+="parseFloat(%s)+" % x
 #                  formulaTot+="0"
 #                  fb.dataFormula('.%s' %attr['codice'], formulaTot,**formulaArgs)
 #              else:
 #                  formulaArgs = dict([(str(x),'^.%s' %x) for x in fields.digest('#a.codice') if x in formula])
 #                  formula = re.sub('[^\s,()*/%+-]+',lambda v:  v.group(0).replace(',','.') if v.group(0).startswith('Math.') else 'parseFloat(%s)' % v.group(0).replace(',','.'),formula)
 #                  #formula = re.sub('[^\s()*/%+-]+',lambda v: 'parseFloat(%s)' % v.group(0),formula)
 #                  fb.dataFormula('.%s' %attr['codice'], formula,**formulaArgs)
 #
 #          
 #          if attr.get('tipo_campo') == 'GR':
 #              pane.iframe(nodeId='chart_iframe2',height='250px', width='99%', border=1,src='^.$chart_url2')
 #              grafico = True
 #          else:
 #              if attr.get('minimo_normale') is not None and attr.get('massimo_normale') is not None:
 #                  div = fb.div(lbl=attr['descrizione'],_class='^.fuori_range_%s' % attr['codice'])
 #              
 #                  div.dataController(""" 
 #                          if(value >= minimo && value <= massimo){
 #                              this.setRelativeData('._'+codice, null);
 #                              this.setRelativeData('.fuori_range_'+codice, 'in_range');
 #                          }else{
 #                              this.setRelativeData('._'+codice, ' *');
 #                              this.setRelativeData('.fuori_range_'+codice, 'fuori_range');
 #                          }
 #                      """,codice=attr['codice'], value='^.%s' %attr['codice'], minimo=attr.get('minimo_normale'), massimo=attr.get('massimo_normale'))
 #                  
 #                  fld = div.child( **kwargs)
 #                  div.span(' <i>['+str(attr.get('minimo_normale'))+' - '+str(attr.get('massimo_normale'))+']</i>')
 #                  div.span(value='^._%s' %attr['codice'] , style='font-weight:bold;font-size:15px')
 #              else:
 #                  fld = fb.child(**kwargs)
 #                  if attr.get('tipo_campo') == 'B':
 #                      lista_check.append(kwargs['lbl'])
 #          
 #          riepilogo = attr.get('riepilogo')
 #          
 #          
 #          
 #          
 #          if (riepilogo =="Si") or riepilogo is None:
 #              if fld is not None:
 #                  validate_call = """function(result,userChange){
 #                      var result = result;
 #                      if(!userChange){
 #                          return;
 #                      }
 #                      var lbl = '%(descrizione)s';
 #                      var chunk = '';
 #                      if((result!=null)&&(result!='')&&!(isNaN(result))){
 #                          var r = this.attr.values?this.widget.getDisplayedValue():result;
 #                          chunk = '<b style="color:rgb(70,70,70);">- %(descrizione)s:</b> '+r;
 #                      }
 #      
 #                      if(this.attr.values){
 #                              this.setRelativeData('.%(codice)s_d?chunk',chunk);
 #                       }else{
 #                              this.setRelativeData('.%(codice)s?chunk',chunk);
 #                      }
 #                  }""" %attr
 #                  fld.attributes['validate_onAccept'] = validate_call
 #      if in_line:
 #          separator="  "
 #      else:
 #          separator=" <br/> "
 #      pane.dataController("""if($2.kw.changedAttr=='chunk'){
 #                              var result = [];
 #                              var chunk;
 #                              data.forEach(function(n){
 #                                  chunk = n.attr.chunk;
 #                                  if((chunk!=null) && (chunk!='')){
 #                                      result.push(chunk);
 #                                  }
 #                              });
 #                              SET %s=result.join(separator);
 #                          }
 #                          """ %(path_fulldescription),data="^%s" %path_databag,separator=separator)
 #      
 #      l_check = ''
 #      if len(lista_check) > 0:
 #          l_check = (',').join(lista_check)
 #      
 #      #pane.dataController("""
 #      #    
 #      #    var arr_check = new Array();
 #      #    if (l_check != '')
 #      #        arr_check = l_check.split(',');
 #      #    for (var i=0;i<arr_check.length;i++){
 #      #        riepilogo = riepilogo.replace(arr_check[i]+':</b> true',arr_check[i]+':</b> Si').replace(arr_check[i]+':</b> false',arr_check[i]+':</b> No').replace(arr_check[i]+':</b>   <br/>',arr_check[i]+':</b> No <br/>');
 #      #    }
 #      #    
 #      #    
 #      #    SET %s = riepilogo;
 #      #"""%(path_fulldescription), riepilogo='^%s'%(path_fulldescription),l_check=l_check, _if='riepilogo')
 #      
 #      if stampabile:
 #          pane.button('Stampa', width='75px', float='right', margin_right='50px', iconClass='icnBasePrinter', action="""
 #              FIRE stampa_record;
 #          """)
 #          if grafico:
 #              pane.dataController("genro.openWindow(genro.makeUrl('/report/stampaRecord',{pkey:pkey, maintable:'go.ricovero', table:table, url_grafico:url, path:'html_res/stampa_record', campo_riepilogo:campo_riepilogo, id:id, descrizione:descrizione}),'Record',{scrollbars:'yes',location:'no'});",pkey="=.ricovero_id", table='=.?table', url='=.$chart_url2', _fired='^stampa_record', campo_riepilogo=path_fulldescription.replace('.',''), id='=.id', descrizione=descrizione)
 #          else:
 #              pane.dataController("genro.openWindow(genro.makeUrl('/report/stampaRecord',{pkey:pkey, maintable:'go.ricovero', table:table, url_grafico:url, path:'html_res/stampa_record', campo_riepilogo:campo_riepilogo, id:id, descrizione:descrizione}),'Record',{scrollbars:'yes',location:'no'});",pkey="=.ricovero_id", table='=.?table', url=False, _fired='^stampa_record', campo_riepilogo=path_fulldescription.replace('.',''), id='=.id', descrizione=descrizione)
    