class GnrCustomWebPage(object):
    py_requires = 'public:Public,gnrcomponents/htablehandler:HTableHandler'

    def windowTitle(self):
        return '!!Categories'

    def main(self, rootBC, **kwargs):
        pane, top, bottom = self.pbl_rootContentPane(rootBC, '!!Categories', margin='10px')
        self.htableHandler(pane, table='flib.category', nodeId='editCategory', rootpath=None,
                           datapath='categories', editMode='bc')

    def editCategory_form(self, parentBC, table=None, disabled=None, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='4px', dbtable=table, disabled=disabled)
        fb.field('child_code', width='5em')
        fb.field('description', colspan=2, width='20em')