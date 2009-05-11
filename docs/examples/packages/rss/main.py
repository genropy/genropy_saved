#!/usr/bin/env python
# encoding: utf-8

class Package(object):
    def config_attributes(self):
        return dict(comment='rss package',
                name_short='rss', name_long='rss', name_full='rss')
        
    def config_db(self, pkg):
        user = pkg.table('user', rowcaption='username',pkey='username')
        user.column('username',len_max='22')
        user.column('password')
        user.column('email')
        
        
        feed = pkg.table('feed', rowcaption='name',pkey='id')
        feed.column('id', len_max='22')
        feed.column('name')
        feed.column('channel')
        feed.column('topic')
        feed.column('url')
        feed.column('user_id').relation('user.username')
        
        article = pkg.table('article', rowcaption='title',pkey='id')
        article.column('id', len_max='22')
        article.column('title')
        article.column('author')
        article.column('abstract')
        article.column('rating','L')
        article.column('date','D')
        article.column('feed').relation('feed.id')
        article.column('url')
        
        
        
        
        
        
        
        
