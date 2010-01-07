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
        movie_selector = left.dbSelect( gnrId='film_selector',
                                        dbtable='video.movie', 
                                        bfield="title",recordpath='movie.record', 
                                        _class='linkerselect'
                                        )
                                        
        pane= layout.contentPane(layoutAlign='client',height='5em', datasource='movie.record')   
        self.movieinfoPane(pane)

        
    def movieinfoPane(self, pane, **kwargs):
        """We define here a box with movie info"""
        movie_info=pane.div( border='inset 1px', height='5em', width='20em', padding='1em', margin='1em', background_color='#CCCCFF')
        movie_info.span(datasource=':title', font_weight='bold', font_size='12pt')
        movie_info.br()
        movie_info.span(datasource=':genre', mask='%s ')
        movie_info.span(datasource=':nationality', mask='(%s ')
        movie_info.span(datasource=':year', mask='-%s)')
        movie_info.br()
        movie_info.span(datasource=':@director.name', mask=' directed by %s ')

        
   
#---- rpc index call -----
