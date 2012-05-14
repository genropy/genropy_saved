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
    index_url='indexcontent.html'
    #showTabs=True
    authTags='user'
    login_title = '!!gnrtutor login' # here the title
    newwindow_title='!!Open new window'# this is the title for new window  (but i don't remember tif it is written in this way.-...)ok
    
    # def loginboxPars(self):
    #     return dict(width='320px',_class='index_loginbox',shadow='5px 5px 20px #555',rounded=10) # Here you can customise look

    def windowTitle(self):
        return '!!Genropy Tutor'

    def windowTitleTemplate(self):
       return 'gnrTutor' # ?? what is the difference between windowTitle


    def loginSubititlePane(self,pane):#here you can define the sub title as you required a 
        pane.div('Please log in User:demo Password:demo',text_align='center',font_size='.9em',font_style='italic',color='#AAAAAA')

    # def rootenvForm(self,fb):
    #     fb.div(lbl='',innerHTML='this is my special text')
    #     fb.parent.parent.div('User:demo',color='#AAAAAA')
    #     fb.parent.parent.div('Password:demo',color='#AAAAAA')

    def onUserSelected(self,avatar,data):
        return {}
        print 'I am in onUserSelected'