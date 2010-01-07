#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo Hello World """

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root,padding='2px')
        root.data('mytable',self.tableData())
        root.data('bottombar.servertime',remote='serverTime')
        root.data('foo.bar',remote='bar')
        root.data('mydata.disk',remote='diskDirectory')
        layout = root.layoutContainer(name='mainContainer', height='100%')
        layout.contentPane(name='top',layoutAlign='top').div('Data source example', _class='demotitle')
        left = layout.contentPane(name='left',layoutAlign='left',width='20%',background_color='silver')
        left.tree(gnrId='tree_data', name ='tree',datasource='*D', root='Client data')
        bottom = layout.contentPane(name='bottom',layoutAlign='bottom',border='1px solid', height='4%')
        orario = bottom.span(datasource='bottombar.servertime' )
        orario.data(remote='serverTime')
        client = layout.contentPane(name='clipane',layoutAlign='client',border='1px solid',padding='2em')
        tbl = client.div(name='table',border='1px solid navy', padding='3px',datasource='mytable').table()
        for x in range(5):
            fp='mytable.r%i.value' % x
            row=tbl.tr(datasource=':r%i' % x)
            row.td('label %i' % x)
            row.td().input(datasource=':value', validate_case="capitalize", validate_len='3,10')
            row.td().button('btn %i' % x, datasource=':btn',onClick="=function(){genro.setData('%s',genro.getData('%s')+'|')}"%(fp,fp))
            row.td().checkBox(datasource=':cb')
            row.td().select(values='[["male","M"],["female","F"]]', datasource=':sex') 
        row = tbl.tr()
        row.td().input(datasource='record.provincia', validate_db="utils.province,pinuccio", validate_case='upper', validate_notNull='Y')
        row.td().span(datasource='pinuccio.descrizione')

        client.button(caption="Server Call", action="alert(genro.serverCall('doThis', {num:21,str:'ciao'}).getItem('dd'))")
        client.button(caption="Server Text", action="alert(genro.serverCall('doThis', {num:21,str:'ciao'}, 'text'))")
        client.button(caption="Server Async", action="genro.serverCall('doThis', {num:21,str:'ciao'}, function(result){alert(result)})")

        client.button(caption="Server Do", action="genro.serverCall('doThis',{num:21,str:'ciao'})")
        
        
        
    def rpc_doThis(self, num, str):
        return '%s *%s' % (str, num)
        #return {'a':'b'}
    
    def rpc_validPiero(self, **kwargs):
        raise GnrWebClientError('vale solo pierone')
    
    def tableData(self):
        mytable=Bag()
        mytable.setItem('r0.value','name 0')
        mytable['r0.btn']='Button 0'
        mytable['r0.cb']=True
        mytable['r0.sex']='M'
        mytable.setItem('r1.value','pierone', _attributes=dict(validate_server='validPiero'))
        
        mytable.setItem('r1.cb',False,_attributes=dict(validate_accept="""function(kw){if (kw.value){var prv='CO'}else{var prv='GE'};
                                                                genro.setData("record.prov",prv);
                                                                }"""))
        mytable['r1.sex']='M'
        mytable['r2.value']='name 2'
        mytable['r2.btn']='Button 2'
        mytable['r2.cb']=True
        mytable['r1.sex']='M'
        mytable['r3.value']='name 3'
        mytable['r4.value']='name 4'
        return mytable
        
    def rpc_serverTime(self):
        return  datetime.datetime.now().strftime('%H:%M:%S')
        
    def rpc_diskDirectory(self):
        return  Bag(dict(root=DirectoryResolver('/')))
    
    def rpc_bar(self):
        return  'hello _ now is :'+datetime.datetime.now().strftime('%H:%M:%S')


