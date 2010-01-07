#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#


""" Hello Pycon """

#------ imports ------




class GnrCustomWebPage(object): 
    
    # ----- Page description -----
              
    def main(self, root, **kwargs):
        layout = root.layoutContainer(height='100%',background_color='silver')
        header = layout.contentPane(layoutAlign='top',  background_color='maroon')
        title = header.div('Movies', color='white', text_align='center', font_size='18pt')
        left = layout.contentPane(layoutAlign='left', width='30em', padding='1em')
        left.span('Select a movie', margin_right='10px')
        movie_selector = left.dbSelect( dbtable='video.movie', 
                                        dbfield="title",
                                        recordpath='film.record',
                                        datasource='film.record', 
                                        _class='linkerselect')

#---- rpc index call -----
