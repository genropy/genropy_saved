#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self,root,cache=False,**kwargs):
        if cache:
            root.script('genro.cache_dbselect = true;')
            
        fb = root.formbuilder(cols=2,border_spacing='10px',datapath='myform')
        
        fb.dbSelect(dbtable='showcase.person',limit='15',value='^.person_id',lbl='Star')
        
        fb.dbSelect(dbtable='showcase.cast',value='^.movie_id',
                    condition='$person_id =:pid',condition_pid='=.person_id',
                    columns='@movie_id.title',rowcaption='@movie_id.title',
                    # you can add the rowcaption attribute, if you do not so...
                    # ...dbSelect take it from the file showcase.cast (if defined)
                    alternatePkey='movie_id',lbl='Movie')
                    
  #     fb.dbSelect(dbtable='showcase.cast',value='^.cast_id',
  #                 lbl='Movie',columns='@movie_id.title',
  #                 condition='$person_id =:pid',
  #                 condition_pid='=.person_id',rowcaption='@movie_id.title',
  #                 auxColumns='@movie_id.nationality',hiddencolumns='$movie_id',
  #                 selected_movie_id='.movie_id')