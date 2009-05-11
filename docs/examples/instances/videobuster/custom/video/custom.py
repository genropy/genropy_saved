#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Saverio Porcari on 2007-05-10.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""


class Package(object):
    def config_attributes(self):
        return dict(comment='Videobuster catalog',level=120)
    
    def config_db_custom(self,pkg):
        director=pkg.getTable('director')
        director.updColumn('year',name_short='Y')
        movie=pkg.getTable('movie')
        movie.column('rating', name_short='rt.',name_long='rating', name_full='Rating', len_max='60', len_min='1',len_show='30')
        vhs = pkg.table('vhs', name_short='Vhs',name_long='Vhs', name_full='Vhs')
        vhs_id = vhs.intColumn('code')
        vhs.pkey('code')
        vhs.column('movieid', name_short='Mid',name_long='Movie id').relate(movie.getColumn('id'))
        vhs.dateColumn('purchasedate', name_short='Pdt',name_long='Purchase date', name_full='Purchase date')
        vhs.column('available', name_short='Avl',name_long='Available', name_full='Is available')
        
    def config_menu():
        pass
        


if __name__ == '__main__':
        main()

