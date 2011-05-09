# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
class GnrCustomWebPage(object):
    py_requires = 'portal_component,foundation/macrowidgets:RichTextEditor'
    css_requires = 'genropynet.css'

    def windowTitle(self):
        return 'GenroPy'

    def main(self, root, **kwargs):
        layout = root.borderContainer(regions='^layout.regions')
        layout.data('layout.regions.top')
        self.index_top(layout.borderContainer(region='top', _class='site_header', height='40px'))
        self.index_left(layout.contentPane(region='left', _class='site_sidebar_left'))
        self.index_right(layout.contentPane(region='right', _class='site_sidebar_right'))
        self.index_center(layout.contentPane(region='center', nodeId='mainstack', _class='site_center site_pane'))

    def index_left(self, pane):
        pass

    def index_right(self, pane):
        pass

    def index_top(self, bc):
        left = bc.contentPane(region='left', _class='site_header_left')
        box = left.div()
        box.span('menu')
        menu = box.menu(modifiers='*')
        menu.menuline('!!New article', action='SET remote_page="new_article";')
        loginstack = 'login'
        if self.user:
            loginstack = 'logout'
        left.dataFormula('loginstack', '"%s"' % loginstack, _onStart=True)
        right = bc.stackContainer(region='right', selectedPage='^loginstack', _class='site_header_right')
        self.loginbox(right.contentPane(pageName='login', datapath='login'))
        self.logoutbox(right.contentPane(pageName='logout'))

    def loginbox(self, pane):
        pane.dataRpc('.result', 'doLogin', login='=.form', btn='^.enter', _onResult='FIRE .afterLogin')
        pane.dataController("genro.dom.effect('bottomMsg','fadeout',{duration:3000,delay:3000});",
                            msg='^error_msg', _if='msg')
        pane.dataController("SET loginstack='logout';", message='=.result.message',
                            _if="message==''", _else="FIRE .error_msg = badUserMsg; SET .form = null;",
                            badUserMsg="!!Incorrect Login", _fired='^.afterLogin')

        fb = pane.formbuilder(cols=4, border_spacing='4px', _class='login',
                              onEnter='FIRE .enter', datapath='.form')
        fb.textbox(value='^.user', ghost='User', width='10em')
        fb.textbox(value='^.password', ghost='Password', lbl_width='1em', type='password',
                   width='10em')
        fb.button('!!Login', baseClass='loginbutton', fire='login.enter')
        fb.button('!!Subscribe', baseClass='loginbutton', action='SET remote_page="subscribe";')

        pane.div('^.error_msg', nodeId='bottomMsg', text_align='center', _class='disclaimer')


    def logoutbox(self, pane):
        pane.dataRecord('user', 'adm.user', username='^login.result.user')
        pane.div('^login.result.user', float='left')
        pane.button('logout', float='right', action='genro.logout();')

    def index_center(self, pane):
        pane.remote('content_caller', page='^remote_page')

    def remote_content_caller(self, pane, page=None, **kwargs):
        getattr(self, page)(pane)

    def subscribe(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='6px', dbtable='adm.user', width='400px', datapath='newuser')
        fb.field('username', autospan=1)
        fb.field('firstname', autospan=1)
        fb.field('lastname', autospan=1)
        fb.textBox(value='^.pwd', lbl='Password', type='password', width='100%')
        fb.textBox(value='^.confirm_pwd', lbl='Confirm Password', type='password', width='100%')

    def new_article(self, pane):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        center = bc.borderContainer(region='center')
        fb = top.formbuilder(cols=1, border_spacing='6px', dbtable='portal.article', width='400px',
                             datapath='newarticle')
        fb.field('subject', autospan=1)
        fb.field('summary', autospan=1)
        fb.field('tags', autospan=1)
        self.RichTextEditor(center, value='^.html', contentPars=dict(region='center'),
                            nodeId='htmlEditor', editorHeight='200px', toolbar=self.rte_toolbar_standard())
                            
        
        