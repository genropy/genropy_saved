# -*- coding: UTF-8 -*-

# ${TM_NEW_FILE_BASENAME}.py
# Created by ${TM_FULLNAME} on ${TM_DATE}.
# Copyright (c) ${TM_YEAR} ${TM_ORGANIZATION_NAME}. All rights reserved.

class GnrCustomWebPage(object):
    py_requires="testhandler:TestHandlerBase"

    def windowTitle(self):
        return ''
         
    def test_${1:testname}(self,pane):
        pass