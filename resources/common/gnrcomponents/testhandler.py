# -*- coding: UTF-8 -*-

# testhandler.py
# Created by Giovanni Porcari on 2010-08-09.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class TestHandler(BaseComponent):
    #py_requires='gnrcomponents/source_viewer/source_viewer:SourceViewer'
    testOnly=False
    dojo_source=True


    def isDeveloper(self):
        return True
        
    def testHandler(self, pane):
        #self.testHandler_headers(pane)
        
        title = pane.div(width='900px', text_align='center', color='#ACACAC', font_size='20pt')
        #TO BE FIXED: title.span(self.__module__.__doc__ or '...missing docline in module...') 
        title.span('Test')
        pane = pane.div(width='900px')
        self.testHandler_loop(pane)
        
        
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
            element = pane.div(border='1px solid gray', margin='5px',
                               rounded=5, shadow='3px 3px 5px gray',
                               datapath='test.%s' % test_name)
            h = element.div()
            h.a('Show Source',href='',float='right',onclick='alert("ggg")',style='cursor:pointer',
                 color='white',font_size='11px',margin_right='5px',margin_top='3px')
            h.div(test_handler.__doc__ or test_name, background_color='#ACACAC',
                  color='white', padding='3px')
                  
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
        