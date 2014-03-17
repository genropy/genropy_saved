# -*- coding: UTF-8 -*-

# login_component.py
# Created by Niso on 2011-03-03.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class LoginPage(BaseComponent):
    css_requires='public'
    
    def loginTitle(self):
        return '!!Login'
        
    def main(self, root, **kwargs):
        self.rootAttributes(root.attributes)
        root.loginFrame(title=self.loginTitle(),shadow='2px 2px 2px gray',rounded=12,
                        gradient_from='black',gradient_to='white',gradient_deg=90,**kwargs)
                        
    def rootAttributes(self,attributes):
        attributes['height'] = '130px'
        attributes['width'] = '250px'
        attributes['margin'] = 'auto'
        attributes['padding'] = '5px'
        
    @struct_method
    def lg_loginFrame(self,pane,title=None,fromPage=None,**kwargs):
        frame = pane.framePane(frameCode='login',datapath='logindata',**kwargs)
        self.layoutAttributes(frame.attributes)
        frame.top.loginTop(title=title)
        frame.loginCenter()
        frame.bottom.loginBottom()
        self._loginController(frame,fromPage=fromPage)
        
    def layoutAttributes(self, attributes):
        pass
        
    @struct_method
    def lg_loginTop(self,pane,title=None):
        pane.slotToolbar('*,title,*',title=title,height='20px')
        
    @struct_method
    def lg_loginBottom(self,pane):
        pane.slotBar('*,messageBox,*',background='transparent',
                        messageBox_subscribeTo='failed_login_msg',color='white',height='12px')
                        
    @struct_method
    def loginCenter(self,frame):
        fb = frame.formbuilder(cols=2, border_spacing='3px',onEnter='PUBLISH login;',margin='auto',
                                    margin_top='15px',fld_line_height='20px',fld_padding='2px',fld_rounded=6)
        fb.textbox(value='^.user',ghost='Username',colspan=2)
        fb.textbox(value='^.password',ghost='Password',type='password')
        frame.button('Entra',action='PUBLISH login;',padding='1px',rounded=10,bottom='3px',right='32px',position='absolute')
        
    def _loginController(self,frame,fromPage=None):
        rpc = frame.dataRpc('dummy','doLogin',subscribe_login=True,login='=logindata',_POST=True)
        rpc.addCallback("""var msg = result.getValue().getItem('message');
                            if(msg===''){
                                if(fromPage){
                                    genro.gotoURL(fromPage);
                                }else{
                                    genro.gotoHome();
                                }
                            }else{
                                PUBLISH failed_login_msg = {message:badUserMsg};
                                SET login = null;
                            }
                            return result;
                            """,badUserMsg="!!User unknown or wrong password",fromPage=fromPage)
