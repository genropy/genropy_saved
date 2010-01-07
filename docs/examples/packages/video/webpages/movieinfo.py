#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#


""" Movie info page """

#------ imports ------




class GnrCustomWebPage(object): 
	
	# ----- Page description -----
	          
    def main(self, root, **kwargs):
		
		# ----- page layout -----
		layout = root.layoutContainer(height='100%',background_color='silver')
		
		# ----- title header ------
		header = layout.contentPane(layoutAlign='top', 
		                            background_color='maroon')
		title = header.div('Movies', color='white', text_align='center', font_size='18pt')
		
		left = layout.contentPane(layoutAlign='left', width='30em', padding='1em')
		left.span('Select a movie', margin_right='10px')
		movie_selector = left.dbSelect(dbtable='video.movie', 
		                               dbfield="title",recordpath='film.record', 
		                               datasource='film.record'
		                               _class='linkerselect')
		
		# ----- client pane with information box ----- 
		client= layout.contentPane(layoutAlign='client')		
		movie_info=client.div(datasource='film.record', border='inset 1px', height='5em', width='20em', padding='1em', margin='1em', background_color='#CCCCFF')
		movie_info.span(datasource=':title', font_weight='bold', font_size='12pt')
		movie_info.br()
		movie_info.span(datasource=':genre', mask='%s ')
		movie_info.span(datasource=':nationality', mask='(%s ')
		movie_info.span(datasource=':year', mask='-%s)')
		movie_info.br()
		movie_info.span(datasource=':@director.name', mask=' directed by %s ')

#---- rpc index call -----
