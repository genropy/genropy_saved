#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage import GnrGenshiPage as page_factory
from gnr.web.gnrwsgisite import httpexceptions
from genshi import HTML


class GnrCustomWebPage(object):
    from tools import codeToPath
    css_requires='website'
    
    def _pageAuthTags(self, method=None, **kwargs):
           return 'user'
    
    def genshi_template(self):
        return 'index.html'
    
    def main(self, rootBC, **kwargs):
        pass

    def getIndexArticles(self,n=None):
        lista = list()
        articles=self.db.table('website.index_article').query(columns='*,@page_id.@folder.code AS folder_code,@page_id.title AS title,@page_id.permalink AS permalink,@page_id.content AS content',order_by='$_row_counter asc',limit=n).fetch()
        for art in articles:
            image=self.db.table('website.media').query(where='page_id=:page_id', page_id=art['page_id'],columns='*,@flib_id.url AS url', order_by='$__ins_ts asc',limit=1).fetch()
            if image:
                image = image[0]['url']
            path=self.codeToPath(art['folder_code'])+art['permalink']
            a=dict(title=art['title'],content=self.tagliaContenuti(paragrafo=art['content']),image=image,path=path)
            lista.append(a)
        return lista
        
    def tagliaContenuti(self,paragrafo=None,caratteri=600):
        if not paragrafo:
            return ''
        try:
            import BeautifulSoup
            lung_par = len(paragrafo) 
            taglio = lung_par 
            continua = '' 
            if lung_par>caratteri:
                indice = caratteri-1 
                while paragrafo[indice] not in ('.','?','!','<','>'):
                    indice = indice+1
                taglio=indice+1
                if paragrafo[indice]=='<':
                    taglio=indice 
                if paragrafo[indice]=='.':
                    indice=indice+1
                    while paragrafo[indice] not in ('<','>'):
                        indice=indice+1
                    if paragrafo[indice]=='>':
                        taglio= indice+1
            soup = BeautifulSoup.BeautifulSoup(paragrafo[0:taglio])
            soup = soup.prettify()
            out=HTML(soup)
        except:
            out='Articolo degradato'
        return out