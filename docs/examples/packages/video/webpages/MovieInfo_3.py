#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#


""" Hello Pycon """

#------ imports ------
from gnr.web.gnrwebcore import GnrWebPage


# ----- GnrWebPage subclass -----

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
                                        datasource='movie.record',
                                        _class='linkerselect')
                                        
        pane= layout.contentPane(layoutAlign='client',height='5em', datasource='movie.record')   
        self.movieinfoPane(pane)
        pane= layout.contentPane(layoutAlign='bottom',height='50%')
        self.directorMovies(pane)
        
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
        
    def directorMovies(self, pane, **kwargs):
        pane=pane.div(margin='6px',border='1px inset',height='100%')
        pane.bagFilteringTable(_class='dojo',
                                datasource='movie.record.@director.@video_movie_director',
                                alternateRows='True',
                                columns='id,title,genre,director,year,nationality')
        
   
#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()