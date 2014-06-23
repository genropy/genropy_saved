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
from gnr.core.gnrbag import Bag
from gnr.core.gnrhtml import GnrHtmlBuilder

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('htmltemplate', pkey='id', name_long='!!Letterhead',
                        name_plural='!!Letterheads', rowcaption='name',noTestForMerge=True)
        self.sysFields(tbl)
        tbl.column('name', name_long='!!Name',validate_notnull=True)
        tbl.column('username', name_long='!!Username')
        tbl.column('version', name_long='!!Version')
        tbl.column('type_code',name_long='Type').relation('letterhead_type.code',relation_name='letterheads',mode='foreignkey',onDelete='raise')
        tbl.column('data', dtype='X', name_long='!!Data', _sendback=True)
        tbl.column('center_height',dtype='I',name_long='!!Center height')
        tbl.column('center_width',dtype='I',name_long='!!Center width')

        tbl.column('based_on',size='22' ,group='_',name_long='!!Based on').relation('htmltemplate.id',relation_name='children',one_one=True,mode='foreignkey',onDelete='raise',deferred=True)
        tbl.column('next_letterhead_id',size='22' ,group='_',name_long='!!Next letterhead').relation('htmltemplate.id',relation_name='previous',one_one=True,mode='foreignkey',onDelete='raise',deferred=True)


    def getTemplate(self,letterhead_id=None,name=None):
        if not(name or letterhead_id):
            return Bag()
        result = Bag()
        if letterhead_id:
            pkeys = self.letterheadChain(letterhead_id)
            f = self.query(where='$id IN :pkeys', pkeys=pkeys, columns='*,$data').fetchAsDict('id')
            if not f:
                return result
            for i,pkey in enumerate(pkeys):
                result.setItem('layer_%i' %i,Bag(f[pkey]['data']))
            if f[letterhead_id]['next_letterhead_id']:
                result['next_letterhead'] = self.getTemplate(f[letterhead_id]['next_letterhead_id'])
            return result
        else:
            templatelist = name.split(',')
            f = self.query(where='$name IN :names', names=templatelist, columns='name,version,data').fetchAsDict(key='name')
            if not f:
                return result
            for i,name in enumerate(templatelist):
                result.setItem('layer_%i' %i,Bag(f[name]['data']))
        return result      

    def letterheadChain(self,letterhead_id):
        result = [letterhead_id]
        based_on = True
        while based_on:
            based_on = self.readColumns(pkey=result[0],columns='$based_on')
            if based_on:
                result = [based_on]+result
        return result

    def getHtmlBuilder(self,letterhead_pkeys=None):
        """Prepare the layout template
        
        :param tpl: the template"""
        
        letterhead_pkeys = letterhead_pkeys.split(',') if isinstance(letterhead_pkeys,basestring) else letterhead_pkeys
        first_letterhead = letterhead_pkeys[0]
        f = self.query(where='$id IN :pk',pk=letterhead_pkeys,bagFields=True).fetchAsDict('id')
        first_letterhead_record = f[first_letterhead]
        if len(letterhead_pkeys) == 1 and first_letterhead_record['based_on']:
            return self.getHtmlBuilder(self.letterheadChain(first_letterhead))
        base_letterhead_bag = Bag()
        base_letterhead_bag.setItem('layer_0',Bag(first_letterhead_record['data']))
        builder = GnrHtmlBuilder(htmlTemplate=base_letterhead_bag)
        builder.initializeSrc()
        height=builder.page_height - builder.page_margin_top - builder.page_margin_bottom
        width=builder.page_width - builder.page_margin_left - builder.page_margin_right
       #page = builder.body.div(height='%imm' %builder.page_height,width='%imm' %builder.page_width,
       #                        position='relative',_class='letterhead_page')

        page = builder.body.div(style="""position:relative;
                                   width:%smm;
                                   height:%smm;
                                   top:0mm;
                                   left:0mm;
                                   """ % (builder.page_width, builder.page_height),
                                   _class='letterhead_page')


        builder.letterhead_root = page.div(style="""position:absolute;
                                   top:%imm;
                                   left:%imm;
                                   right:%imm;
                                   bottom:%imm;""" % (
                            builder.page_margin_top, builder.page_margin_left,
                            builder.page_margin_right, builder.page_margin_bottom))

        for i,pkey in enumerate(letterhead_pkeys):
            regions = self.letterhead_layer(builder, Bag(f[pkey]['data']),width=width,height=height,count=i)
        builder._regions = regions
        regions['center_center'].attributes['content_node'] ='t'
        return builder
                    
    def letterhead_layer(self,builder,letterheadBag,width=None,height=None,count=None):
        layout = builder.letterhead_root.layout(top=0,left=0,border=0,width=width,height=height,z_index=count)
        regions = dict(center_center=layout)
        if letterheadBag['main.design'] == 'headline':
            for region in ('top', 'center', 'bottom'):
                height = float(letterheadBag['layout.%s?height' % region] or 0)
                if region == 'center' or height:
                    row = layout.row(height=height)
                    for subregion in ('left', 'center', 'right'):
                        width = float(letterheadBag['layout.%s.%s?width' % (region, subregion)] or 0)
                        if subregion == 'center' or width:
                            innerHTML = letterheadBag['layout.%s.%s.html' % (region, subregion)] or None
                            if innerHTML:
                                innerHTML = "%s::HTML" % innerHTML
                            regions['%s_%s' % (region, subregion)] = row.cell(content=innerHTML, width=width, border=0,
                                                                                overflow='hidden')
        elif letterheadBag['main.design'] == 'sidebar':
            mainrow = layout.row(height=0)
            for region in ('left', 'center', 'right'):
                width = float(letterheadBag['layout.%s?width' % region] or 0)
                if region == 'center' or width:
                    col = mainrow.cell(width=width, border=0).layout()
                    for subregion in ('top', 'center', 'bottom'):
                        height = float(letterheadBag['layout.%s.%s?height' % (region, subregion)] or 0)
                        if subregion == 'center' or height:
                            row = col.row(height=height)
                            innerHTML = letterheadBag['layout.%s.%s.html' % (region, subregion)] or None
                            if innerHTML:
                                innerHTML = "%s::HTML" % innerHTML
                            regions['%s_%s' % (region, subregion)] = row.cell(content=innerHTML, border=0,overflow='hidden')
        return regions


    def onDuplicating(self,record):
        record['name'] = '%s (copy)' %record['name']

    def updateCenterSize(self,record):
        pass
        
    def trigger_onInserting(self,record):
        self.updateCenterSize(record)

    def trigger_onUpdating(self,record=None,old_record=None):
        self.updateCenterSize(record)
    