#!/usr/bin/python

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/doc_handler/doc_handler:DocHandler"
    documentation=True
    def main(self,root,**kwargs):
        root.div("DocItem")
