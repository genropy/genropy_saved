#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable='showcase.cast' # puts in every formbuilder of this webpage the value of showcast.case in dbtable --> dbtable = 'showcase.cast'
    
    def main(self, root, **kwargs):
    #   fb = root.formbuilder(cols=1, datapath='xxx')
        fb = root.formbuilder(cols=1, dbtable='showcase.cast', datapath='xxx')
        
        fb.dbCombobox(lbl='dbselect in form builder',dbtable='showcase.movie',value='^dbcombo.value')

    #    fb.field('showcase.cast.movie_id', lbl='field in fb',validate_notnull=True,validate_notnull_error='!!Required')
    #    fb.div(lbl='field con div', datapath='xxy').field('showcase.cast.movie_id')
    #    fb.div(lbl='dbsel con div', datapath='xxz').dbselect(dbtable='showcase.movie', value='^dbselect.m2',  )