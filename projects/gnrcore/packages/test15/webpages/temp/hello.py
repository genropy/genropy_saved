# -*- coding: UTF-8 -*-

# hello.py
# Created by Francesco Porcari on 2010-08-19.
# Copyright (c) 2010 Softwell. All rights reserved.

"""hello"""

class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        root.div(height='100px',width='100px',background='red',subscribe_ondialog_open='genro.dlg.alert($1.msg)')

  #  def main_root(self, root, **kwargs):
  #      root.data('prova',12)
  #     #tc = root.tabContainer(connect_startup="genro.dom.autoSize(this.widget);")
  #     #self.page1(tc.contentPane(title='page1').div(display='inline-block',padding='30px',position='relative'))
  #     #self.page2(tc.contentPane(title='page2').div(display='inline-block',padding='30px',position='relative'))
        
    def page1(self,pane):
        fb = pane.formBuilder(background='red',cols=3)
        fb.div(width='20px',background='lime',height='30px',lbl='aaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaaaaa')
        fb.div(width='30px',background='lime',height='30px',lbl='aa')
        fb.div(width='60px',background='lime',height='30px',lbl='aaaqqq')
        fb.div(width='10px',background='lime',height='30px',lbl='aaaqqqqq')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        pane.button('piero')
        pane.div(background='gray',height='30px',width='30px',right='2px',bottom='2px',position='absolute')
        
    def page2(self,pane):
        fb = pane.formBuilder(background='red',cols=2)
        fb.div(width='20px',background='lime',height='30px',lbl='aaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaaaaa')
        fb.div(width='30px',background='lime',height='30px',lbl='aa')
        fb.div(width='60px',background='lime',height='30px',lbl='aaaqqq')
        fb.div(width='10px',background='lime',height='30px',lbl='aaaqqqqq')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        fb.div(width='50px',background='lime',height='30px',lbl='aaaaaa')
        
    def __main(self, root, **kwargs):
        box = root.div(border='1px solid gray',display='inline-block',margin='20px',background='#999',rounded=6)#alfa
        attrbox=dict(display='inline-block',position='relative',padding_left='18px',
                        border_right='1px solid gray',padding_right='18px')
        attrtext = dict(style='line-height:20px')
        button = box.div(**attrbox)#beta
        button.div('Pippo',**attrtext)#gamma
        button.div(_class='iframetab_button iframeclose',position='absolute',right='1px',top='1px')#a
        button.div(_class='iframetab_button iframereload',position='absolute',right='1px',bottom='1px')#b
        
        button = box.div(**attrbox)
        button.div('Paperino',**attrtext)
        button.div(_class='iframetab_button iframeclose',position='absolute',right='1px',top='1px')
        button.div(_class='iframetab_button iframereload',position='absolute',right='1px',bottom='1px')
                
        attrbox.pop('border_right')
        button = box.div(**attrbox)
        button.div('ajhghgkjhgkjhgkjhk',**attrtext)
        button.div(_class='iframetab_button iframeclose',position='absolute',right='1px',top='1px')
        button.div(_class='iframetab_button iframereload',position='absolute',right='1px',bottom='1px')
        
    def main_(self, root, **kwargs):
        bc = root.borderContainer(_class='hideSplitter')
        top = bc.contentPane(region='top',border='1px solid gray',margin='1px',height='30px').borderContainer()
        left = bc.borderContainer(region='left',width='200px',splitter=True,border='1px solid gray',margin='1px',margin_right='-1px')
        left.contentPane(region='bottom',background='silver',height='20px')
        center = bc.borderContainer(region='center',border='1px solid gray',margin='1px',margin_left='-1px')
        center.contentPane(region='top',height='20px',background='silver')
        center.contentPane(region='bottom',height='20px',background='silver')
        center.contentPane(region='center',background='whitesmoke')
        