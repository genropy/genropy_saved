# -*- coding: UTF-8 -*-
# 
"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,public:Public"
    #css_requires = 'rich_edit'
    #js_requires = 'ckeditor/ckeditor'
    
    def _test_1_plain(self, pane):
        """Set in external store"""
        bc=pane.borderContainer(height='400px')
        bc.contentPane(region='center').ckeditor(value='^.text', nodeId='ckeditor',height='100%')
        bc.contentPane(region='bottom',height='100px',splitter=True).simpleTextArea(value='^.text',height='100%')
                
    def test_1_constrain(self, pane):
        fb = pane.formbuilder(cols=2,border_spacing='3px')
        fb.textbox(value='^.height',lbl='Height')
        fb.textbox(value='^.width',lbl='Width')
        pane.ckeditor(value='^.testdata',constrain_height='^.height',
                      config_stylesSet='/_site/styles/style_pippo.js',
                      constrain_width='^.width',constrain_border='1px solid red')


    def test_2_stylegroup(self, pane):
        fb = pane.formbuilder(cols=2,border_spacing='3px')
        fb.textbox(value='^.height',lbl='Height')
        fb.textbox(value='^.width',lbl='Width')
        pane.ckEditor(value='^.testdata',stylegroup='base',contentsCss='/_rsrc/common/public.css')

  
    #def main(self, pane):
    #    """Set in external store"""
    #    bc=pane.borderContainer(datapath='test')
    #    #bc.contentPane(region='top',splitter=True,height='150px',overflow='hidden').ckeditor(value='^.textTop', nodeId='ckeTop')
    #   #bc.contentPane(region='left',splitter=True,width='25%',overflow='hidden').ckeditor(value='^.textLeft', nodeId='ckeLeft')
    #   #bc.contentPane(region='right',splitter=True,width='25%',overflow='hidden').ckeditor(value='^.textRight', nodeId='ckeRight')
    #   #bc.contentPane(region='bottom',splitter=True,height='150px',overflow='hidden').ckeditor(value='^.textBottom', nodeId='ckeBottom')
    #    bc.contentPane(region='center',overflow='hidden').ckeditor(value='^.textCenter', nodeId='ckeCenter')
    #    #bc.contentPane(region='bottom',height='100px',splitter=True).simpleTextArea(value='^.textCenter',height='100%')
                