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
		root.div(background_color='red').h1('Hello Pycon',text_align='center')
   
#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()