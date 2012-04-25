# -*- coding: UTF-8 -*-

"""
examplehandler.py
Created by Giovanni Porcari on 2010-08-09.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
import sys
import inspect
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


class ExampleHandler(BaseComponent):
    exampleOnly=False
    dojo_source=True
    css_requires = 'pygmentcss/friendly'


    def isDeveloper(self):
        return True
        
    def exampleHandler(self, pane):
        
        self.exampleHandler_headers(pane)
        
        title = pane.div(width='900px', text_align='center', color='#ACACAC', font_size='20pt')
        moduledoc=sys.modules[self.__module__].__doc__ or '...missing docline in module...'
        title.span(moduledoc)
        pane = pane.div(width='900px')
        self.exampleHandler_loop(pane)
        
    def exampleHandler_headers(self, pane):
        header = pane.div(width='900px', margin='5px')


    def exampleHandler_loop(self, pane):
        def skip_example(example_name):
            if not self.exampleOnly:
                return False
            if isinstance(self.exampleOnly, basestring):
                self.exampleOnly = [self.exampleOnly]
            for exampleOne in self.exampleOnly:
                if exampleOne in example_name:
                    return False
            return True
        example_to_do = [(n,getattr(self,n)) for n in dir(self) if hasattr(getattr(self,n),'isExample')]
        example_to_do.sort(lambda a,b: a[1].example_code >  b[1].example_code) #
        for example_name,example_handler in example_to_do:
            if skip_example(example_name):
                continue
            self.exampleBody(pane,example_name=example_name,example_handler=example_handler)

    def exampleBody(self,pane,example_name=None,example_handler=None):
        bc=pane.borderContainer(border='1px solid gray', margin='5px',height='%spx' %example_handler.example_height,background_color='white',
                           rounded=5, shadow='3px 3px 5px gray',
                           datapath='example.%s' % example_name)
        top=bc.contentPane(region='top',border_bottom='1px solid silver')
        
        
        top.div(example_handler.__doc__ or '...missing example docline...',margin_left='1em')

        ##bottom=bc.contentPane(region='bottom')
       # bottom.div("Here we will put commands as show source or other stuff",margin_left='1em')
        center=bc.tabContainer(region='center')
        p1=center.contentPane(title='Example')
        p2=center.contentPane(title='Source Code')
       # h = element.div()
       # h.a('Show Source',href='',float='right',onclick='alert("ggg")',style='cursor:pointer',
       #      color='white',font_size='11px',margin_right='5px',margin_top='3px')
       # h.div(example_handler.__doc__ or example_name, background_color='#ACACAC',
       #       color='white', padding='3px')
       #       
       # element = element.div(padding='5px')
        example_handler(p1)
        source=inspect.getsource(example_handler).split('\n')
        source.pop(0)
        source='\n'.join(source)
        source=highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
        p2.div(source,_class='codehilite')


        
class ExampleHandlerBase(ExampleHandler):
    def main_root(self, root, **kwargs):
        if self._call_args:
            if '*' in self._call_args:
                self.exampleOnly = False
            else:
                self.exampleOnly = ['_%s_' % str(a) for a in self._call_args]
        self.exampleHandler(root)
        
class ExampleHandlerFull(ExampleHandler):
    def main(self, root, **kwargs):
        if self._call_args:
            if '*' in self._call_args:
                self.exampleOnly = False
            else:
                self.exampleOnly = ['_%s_' % str(a) for a in self._call_args]
        self.exampleHandler(root)
