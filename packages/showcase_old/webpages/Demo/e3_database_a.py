#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


class GnrCustomWebPage(object):
    py_requires='demo:Demo'
    
    def main(self, root, **kwargs):
        root.dbSelect(value='^anagrafica.id', dbtable='assopy.anagrafica',
                             width='20em',margin='10px')
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
    
    
    
    
    