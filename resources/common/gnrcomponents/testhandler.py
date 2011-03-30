# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-09.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class TestHandler(BaseComponent):
    testOnly=False
    def windowTitle(self):
        return 'Test: %s' % self.__module__.__doc__ or 'unnamed'
        
    def testHandler(self, pane):
        self.testHandler_headers(pane)
        
        #pane.div(height='12px',width='12px',position='absolute',top='2px',right='2px',background='red',nodeId='rpcpulser',opacity=0)
        title = pane.div(width='900px', text_align='center', color='#63B8F7', font_size='20pt')
        title.span(self.__module__.__doc__ or '...missing docline in module...')
        pane = pane.div(width='900px')
        self.testHandler_loop(pane)
        
    def testHandler_headers(self, pane):
        header = pane.div(width='900px', margin='5px')
        header.div('Dojo version :', float='left', margin_top='7px', color='gray')
        pane.data('gnr.dojo_version', '1.5')
        mdiv = header.dropdownbutton(label='^gnr.dojo_version', float='left')
        m = mdiv.menu(action='SET gnr. dojo_version=$1.label')
        m.menuline('1.1')
        m.menuline('1.5')
        pane.data('gnr.dojo_theme', 'claro')
        mdiv = header.dropdownbutton(label='^gnr.dojo_theme', float='right', margin_right='10px', padding_top='1px',
                                     padding_bottom='1px')
        header.div('Dojo theme :', float='right', margin_top='7px', color='gray')
        m = mdiv.menu(action='SET gnr.dojo_theme=$1.label')
        m.menuline('Claro')
        m.menuline('Tundra')
        m.menuline('Soria')
        
    def testHandler_loop(self, pane):
        def skip_test(test_name):
            if not self.testOnly:
                return False
            if isinstance(self.testOnly, basestring):
                self.testOnly = [self.testOnly]
            for testOne in self.testOnly:
                if testOne in test_name:
                    return False
            return True
        test_to_do = [n for n in dir(self) if n.startswith('test_')]
        test_to_do.sort()
        for test_name in test_to_do:
            if skip_test(test_name):
                continue
            test_handler = getattr(self, test_name)
            element = pane.div(border='1px solid gray',margin='5px',
                               rounded=5,shadow='3px 3px 5px gray',
                               datapath='test.%s' % test_name)
            h = element.div()
            h.a('Source', href='', float='right', onclick='alert("ggg")', color='white', font_size='10px',
                margin_right='5px', margin_top='3px', style='cursor:pointer')
            h.div(test_handler.__doc__ or test_name,background_color='#63B8F7',
                  color='white',padding='3px')
            
            element = element.div(padding='5px')
            test_handler(element)

class TestHandlerBase(TestHandler):
    def main_root(self, root, **kwargs):
        if self._call_args:
            if '*' in self._call_args:
                self.testOnly = False
            else:
                self.testOnly = ['_%s_' % str(a) for a in self._call_args]
        self.testHandler(root)

class TestHandlerFull(TestHandler):
    def main(self, root, **kwargs):
        if self._call_args:
            if '*' in self._call_args:
                self.testOnly = False
            else:
                self.testOnly = ['_%s_' % str(a) for a in self._call_args]
        self.testHandler(root)
