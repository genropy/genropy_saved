#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
"""
index.py

Created by Jeff Edwards on 2009-10-01.
Copyright (c) 2012 Softwell. All rights reserved.
"""


# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url='genropynet.html'
    #showTabs=True
    authTags='user'
    auth_workdate = 'superuser'

    login_title = '!!Genropy Net' # here the title
    newwindow_title='!!Open new window'# this is the title for new window  (but i don't remember tif it is written in this way.-...)ok
    

    def windowTitle(self):
        return '!!Genropy'

    def windowTitleTemplate(self):
       return 'Genropy $workdate' 


    def loginSubititlePane(self,pane):#here you can define the sub title as you required a 
        pane.div('User:demo Password:demo',text_align='center',font_size='.9em',font_style='italic',color='#AAAAAA')

   # def onUserSelected(self,avatar,data):
   #     if avatar.user_tags=='demo':
   #         data['custom_index'] = 'demo'
#
