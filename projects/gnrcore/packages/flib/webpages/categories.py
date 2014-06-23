class GnrCustomWebPage(object):
    py_requires = 'public:Public,gnrcomponents/htablehandler:HTableHandler'

    def windowTitle(self):
        return '!!Categories'

    def main(self, root, **kwargs):
        frame = root.rootContentPane()
        self.htableHandler(frame, table='flib.category', nodeId='editCategory', rootpath=None,
                           datapath='categories', editMode='bc')

    def editCategory_form(self, frame, table=None, disabled=None, **kwargs):
        pane = frame.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='4px', dbtable=table, disabled=disabled)
        fb.field('child_code', width='5em')
        fb.field('description', colspan=2, width='20em')