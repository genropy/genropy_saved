#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Saverio Porcari on 2007-05-10.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

class Package(object):
    def config_attributes(self):
	return dict(comment='A package for video catalog management',
		    name_short='video',
		    name_long='Video Catalog', 
		    name_full='Video Catalog')
        	
class Table_director(object):
    def config_db(self, pkg):
        director = pkg.table('director', name_short='Dir', name_long='Director', 
                             rowcaption='name,year:%s (%s)')
        dir_id = director.intColumn('id')
        director.pkey('id')
        director.column('name', name_short='N.', name_long='Name')
        director.intColumn('year', name_short='Yr', name_long='Birth Year')
        director.column('nationality', name_short='Ntl',name_long='Nationality')

class Table_dvd(object):
    def config_db(self, pkg):
	dvd = pkg.table('dvd', name_short='Dvd', name_long='Dvd')
        dvd_id = dvd.intColumn('code')
        dvd.pkey('code')
        dvd.column('T', 'movieid', name_short='Mid', name_long='Movie id').relate(movie_id)
        dvd.column('R', 'movieid', name_short='Mid', name_long='Movie id').relate(movie_id)
        dvd.column('A', 'movieid', name_short='Mid', name_long='Movie id').relate(movie_id)
        dvd.column('A', 'movieid', name_short='Mid', name_long='Movie id').relate(movie_id)
        dvd.column('movieid', name_short='Mid', name_long='Movie id').relate(movie_id)
        dvd.dateColumn('purchasedate', name_short='Pdt', name_long='Purchase date')
        dvd.column('available', name_short='Avl', name_long='Available')

class Table_movie(object):
    def config_db(self, pkg):
	movie = pkg.table('movie', name_short='Mv',name_long='Movie', rowcaption='title')
        movie_id = movie.intColumn('id')
        movie.pkey('id')
        movie.column('title', name_short='Ttl.',name_long='Title',
                                validate_case='capitalize', validate_len='3,40')
        movie.column('genre', name_short='Gnr',name_long='Genre',
                                validate_case='upper', validate_len='3,10')
        movie.column('director', name_short='Dir',name_long='Director').relate(dir_id)
        movie.intColumn('year', name_short='Yr',name_long='Year')
        movie.column('nationality', name_short='Ntl', name_long='Nationality')
        movie.column('description', name_short='Dsc', name_long='Movie description')


    def listform_base(self):
        return {'columns': """title,genre,@director.name,year"""}
    
    def inputform_base(self):
        return {'columns': """id,title,genre,director,@director.name,year,nationality,description"""}
        
if __name__ == '__main__':
        main()
