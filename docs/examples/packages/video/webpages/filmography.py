#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#


""" Movie info page """

#------ imports ------




class GnrCustomWebPage(object): 
	
	# ----- Page description -----
	          
    def main(self, root, **kwargs):
		
		root = self.rootLayoutContainer(root,padding='2px')
		
		# ----- page layout -----
		layout = root.layoutContainer(height='100%',background_color='silver')
		
		# ----- title header ------
		header = layout.contentPane(layoutAlign='top', 
		                            background_color='maroon')
		title = header.div('Movies', color='white', text_align='center', font_size='18pt')
		
		left = layout.contentPane(layoutAlign='top', width='30em', padding='1em')
		left.span('Select a director', margin_right='10px')
		movie_selector = left.dbSelect(gnrId='director_selector',
		                               dbtable='video.director', 
		                               dbfield="name",recordpath='director.record', 
		                               _class='linkerselect')
		
		# ----- client pane with information box ----- 
		client= layout.contentPane(layoutAlign='client')		
		ft = client.bagFilteringTable(gnrId='filmography',
                                      _class='dojo',
                                      datasource='director.record.@video_movie_director',
                                      alternateRows='True', columns='id,title,genre,director,year,nationality')

		bottom = layout.contentPane(layoutAlign='bottom', height='40%', padding='5px')
		inputfield = bottom.textarea(height='100%', width='100%',datasource='director.record.@video_movie_director')

#---- rpc index call -----
