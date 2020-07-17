# -*- coding: utf-8 -*-
            
class GnrCustomWebPage(object):
    py_requires = 'plainindex'
    
    def main_root(self,root,**kwargs):
        bc = root.borderContainer(height='100%', text_align='center', background_color='#0a1632')
        bc.img(src='/_rsrc/common/html_pages/images/genropy-checkinstall.gif', width='100%', max_width='1500px')