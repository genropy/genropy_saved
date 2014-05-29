# -*- coding: UTF-8 -*-
            
class GnrCustomWebPage(object):
    py_requires = 'source_viewer'
    
    def main(self,root,**kwargs):
        root.div('Some Genropy stuff',margin='10px',font_size='24px',
                                      color='#444') 
        #we receive a root and we add a div with a content and
        #some attributes.
        
        container=root.div(height='150px',width='300px',margin='10px',
                         border='1px solid gray',rounded='4') 
        #we add now to the root a div that has not a content, just attributes.
        #now this div is in a python variable named 'container'
        #we can now put some elements in container
                         
        for j in range(98):
            container.div(height='15px',width='15px',background='red',
                       shadow='2px 2px 3px #666',margin='3px',
                       rounded='4',float='left')
        
        mytable=root.table(margin='10px',background='#666',
                           border_spacing=0,border_collapse='collapse')
        tbody=mytable.tbody(font_size='10px',color='white')
        for r in range (10):
            row=tbody.tr()
            for c in range (10):
                row.td(padding='2px').div('cell<br/>%i-%i'%(r,c),padding='2px',
                         rounded=4,border='1px solid white')
