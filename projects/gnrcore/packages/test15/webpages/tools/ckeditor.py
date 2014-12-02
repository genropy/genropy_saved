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

    def test_4_simpleTextAreaEditor(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.quickEditor(value='^.test',connect_onBlur='console.log("blurring",evt,this)',
                        height='30px',
                        lbl='test')
        fb.textbox(value='^.aaa',lbl='field 2')
        fb.textbox(value='^.ooo',lbl='field 3')

    def test_5_simpleTextAreaInGrid(self,pane):
        grid = pane.contentPane(region='center').quickGrid(value='^.griddata',
                        height='150px',width='700px' ,border='1px solid silver',
                        default_description='<span style="color:red">ciao</span> come <i>va?</i>'
                        #connect_onCellDblClick='console.log("sss")'
                        )
        grid.tools('addrow,delrow')
        grid.column('location',name='Location',width='15em',edit=dict(tag='dbselect',dbtable='glbl.provincia'))
        grid.column('description',name='Description',width='30em',edit=dict(tag='quickEditor'))
        grid.column('spam',name='Spam',width='8em',edit=True)
