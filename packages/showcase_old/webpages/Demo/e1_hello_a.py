#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


class GnrCustomWebPage(object):
    
    def main_root(self, root, **kwargs):
        self.pkg_defined_method()
        root.div('Hello assopy', font_size='40pt', 
                        border='3px solid yellow', padding='20px')
