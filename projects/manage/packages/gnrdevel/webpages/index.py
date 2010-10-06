# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'public'
    
    def main(self, rootBC, **kwargs):
        center, _top, _bottom = self.pbl_rootBorderContainer(rootBC, margin="1em", **kwargs)
