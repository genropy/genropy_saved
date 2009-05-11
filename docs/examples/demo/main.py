#!/usr/bin/env python
# encoding: utf-8

class Package(object):
    def config_attributes(self):
        return dict(comment='A package for video catalog management',
            name_short='demo',
            name_long='Video Catalog', 
            name_full='Video Catalog')
            
   # def authMe(self, user):
   #     if user=='Me':
   #         return {'pwd':'me', 'tags':'me'}
   #         
    def config_db(self,pkg):
        #you can describe here your database or separate table into classes
        pass
        
class Table_people(object):
    def config_db(self,pkg):
        people = pkg.table('people', name_short='people', name_long='People', 
                             rowcaption='name,year:%s (%s)', pkey='id')
        people.column('id', 'L')
        people.column('name', name_short='N.', name_long='Name')
        people.column('year', 'L', name_short='Yr', name_long='Birth Year')
        people.column('nationality', name_short='Ntl',name_long='Nationality')
        
class Table_cast(object):
    def config_db(self,pkg):
        cast = pkg.table('cast', name_short='cast', name_long='Cast', 
                             rowcaption='', pkey='id')
        cast.column('id', 'L')
        cast.column('movie_id','L', name_short='Mid', 
                               name_long='Movie id').relation('movie.id')
        cast.column('person_id','L',name_short='Prs', 
                               name_long='Person id').relation('people.id')
        cast.column('role', name_short='Rl.',name_long='Role')
        cast.column('prizes', name_short='Priz.',name_long='Prizes', size='40')

class Table_movie(object):
    def config_db(self,pkg):
        movie = pkg.table('movie', name_short='Mv',name_long='Movie',
                           rowcaption='title', pkey='id')
        movie.column('id', 'L')
        movie.column('title', name_short='Ttl.',name_long='Title',
                                validate_case='capitalize', validate_len='3,40')
        movie.index('title', 'i_title',  unique='y')
        movie.column('genre', name_short='Gnr',name_long='Genre',
                                validate_case='upper', validate_len='3,10',indexed='y')
        movie.column('year', 'L', name_short='Yr',name_long='Year',indexed='y')
        movie.column('nationality', name_short='Ntl', name_long='Nationality')
        movie.column('description', name_short='Dsc', name_long='Movie description')
        
class Table_dvd(object):
    def config_db(self,pkg):
        dvd = pkg.table('dvd', name_short='Dvd', name_long='Dvd', pkey='code')
        dvd_id = dvd.column('code', 'L')
        dvd.column('movie_id', name_short='Mid', name_long='Movie id').relation('movie.id')
        dvd.column('purchasedate', 'D', name_short='Pdt', name_long='Purchase date')
        dvd.column('available', name_short='Avl', name_long='Available')
        