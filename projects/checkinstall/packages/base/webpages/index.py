# -*- coding: utf-8 -*-
            
class GnrCustomWebPage(object):
    py_requires = 'plainindex'
    
    def main_root(self,root,**kwargs):
        root.h1('Yay!', text_align='center')
        root.div('Genropy installation was succesful',text_align='center')