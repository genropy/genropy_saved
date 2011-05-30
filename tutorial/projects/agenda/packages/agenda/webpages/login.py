# -*- coding: UTF-8 -*-

# login.py
# Created by Filippo Astolfi on 2011-03-03.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='login_component:LoginPage'
    
    def loginTitle(self):
        return '!!Login Agenda'
        
    # use this to let the login_component be passive (hide the main method)
    def layoutAttributes(self, attributes):
        attributes['gradient_from'] = 'teal' # add other attributes...
        
    # use this to let the login_component be active (hide the layoutAttrbutes method)
    def main_(self,root,**kwargs):
        bc = root.borderContainer()
        bc.loginFrame(title='Login Agenda',shadow='2px 2px 2px gray',
                      region='center',rounded=12,
                      height='300px',width='400px',margin='auto',
                      gradient_from='green',gradient_to='white',
                      gradient_deg=180,**kwargs)