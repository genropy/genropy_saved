# -*- coding: UTF-8 -*-
# 
"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,public:Public,gnrcomponents/filepicker:FilePicker"
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

    def test_3_gallery_handler(self,pane):
        frame = pane.framePane(height='300px')
        bar = frame.top.slotToolbar('*,xxx,5')
        bar.dataFormula('^testpath','p',_onStart=True,p='')
        bar.xxx.imgPickerPalette(folders='rsrc:common/html_pages/images:Image HTML,rsrc:common/icons:Icons',dockButton=True)
        frame.center.contentPane(overflow='hidden').ckEditor(value='^.testgallery')