# -*- coding: utf-8 -*-
# 
"""ClientPage tester"""

from builtins import object
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
                    config_disableNativeSpellChecker=False,
                      config_stylesSet='/_site/styles/style_pippo.js',
                      constrain_width='^.width',constrain_border='1px solid red')


    def test_2_stylegroup(self, pane):
        fb = pane.formbuilder(cols=2,border_spacing='3px')
        fb.textbox(value='^.height',lbl='Height')
        fb.textbox(value='^.width',lbl='Width')
        pane.ckEditor(value='^.testdata',stylegroup='base',contentsCss='/_rsrc/common/public.css')

    def test_6_resize(self, pane):
        bc = pane.borderContainer(height='500px',width='600px')
        bc.contentPane(region='left',width='100px',splitter=True,background='red')
        bc.contentPane(region='center').ckEditor(value='^.testdata')

    def test_3_gallery_handler(self,pane):
        frame = pane.framePane(height='300px')
        bar = frame.top.slotToolbar('*,xxx,5')
        bar.dataFormula('^testpath','p',_onStart=True,p='')
        bar.xxx.imgPickerPalette(folders='rsrc:common/html_pages/images:Image HTML,rsrc:common/icons:Icons',dockButton=True)
        frame.center.contentPane(overflow='hidden').ckEditor(value='^.testgallery')

    def test_4_simpleTextAreaEditor(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.quickEditor(value='^.test',nodeId='aaa',
                        height='100px',
                        width='300px',
                        lbl='test')
        fb.button('focus',action='genro.nodeById("aaa").externalWidget.focus();')
        fb.textbox(value='^.aaa',lbl='field 2')
        fb.textbox(value='^.ooo',lbl='field 3')

    def test_7_simpleTextAreaEditor(self,pane):
        pane.div(_class='quickEditor',height='100px',width='400px').ckEditor(value='^.ccc',
                    constrain_margin_top='1px',
                    constrain_margin='2px',
                    toolbar=False)

    def test_5_simpleTextAreaInGrid(self,pane):
        grid = pane.contentPane(region='center').quickGrid(value='^.griddata',

                        height='500px',width='700px' ,border='1px solid silver',
                        default_description='<span style="color:red">ciao</span> come <i>va?</i>'
                        #connect_onCellDblClick='console.log("sss")'
                        )
        grid.tools('addrow,delrow')
        grid.column('location',name='Location',width='15em',edit=dict(tag='dbselect',dbtable='glbl.provincia'))
        grid.column('description',name='Description',width='30em',edit=dict(tag='quickEditor'))
        grid.column('spam',name='Spam',width='8em',edit=True)
