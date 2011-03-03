# -*- coding: UTF-8 -*-

# login_component.py
# Created by Niso on 2011-03-03.
# Copyright (c) 2011 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class LoginPage(BaseComponent):
    css_requires='public'
    
    def loginTitle(self):
        return '!!Login'
        
    def rootWidget(self,root,**kwargs): # def rootWidget(self,root,region='center',nodeId='_pageRoot')
        return root.framePane(frameCode='login',datapath='logindata',height='130px',width='250px',
                              margin='auto',shadow='2px 2px 2px gray',rounded=12,
                              gradient_from='black',gradient_to='white',gradient_deg=90,**kwargs)
    
    def main(self, frame, fromPage=None, **kwargs):
        self.layoutAttributes(frame.attributes)
        self.loginTop(frame.top)
        self.loginCenter(frame)
        self.loginBottom(frame.bottom)
        self.loginController(frame,fromPage=fromPage)
                              
    def layoutAttributes(self,attributes):
        #attributes[height] = '1000px'
        pass
        
    def loginTop(self,pane):
        pane.slotToolbar('*,title,*',title=self.loginTitle(),height='20px')
        
    def loginBottom(self,pane):
        pane.slotBar('*,messageBox,*',background='transparent',
                        messageBox_subscribeTo='failed_login_msg',color='white',height='12px')
                        
    def loginController(self,frame,fromPage=None):
        rpc = frame.dataRpc('dummy','doLogin',subscribe_login=True,login='=logindata',_POST=True)
        rpc.addCallback("""var msg = result.getValue().getItem('message');
                            if(msg==''){
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
    
    def loginCenter(self,frame):
        fb = frame.formbuilder(cols=2, border_spacing='3px',onEnter='PUBLISH login;',margin='auto',
                                    margin_top='15px',fld_line_height='20px',fld_padding='2px',fld_rounded=6)
        fb.textbox(value='^.user',ghost='Username',colspan=2)
        fb.textbox(value='^.password',ghost='Password',type='password')
        frame.button('Entra',action='PUBLISH login;',padding='1px',rounded=10,bottom='3px',right='32px',position='absolute')