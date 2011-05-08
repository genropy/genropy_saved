# -*- coding: UTF-8 -*-

# update_doc.py
# Created by Roberto Lupi on 2010-10-05.
# Copyright (c) 2010 MedMedia. All rights reserved.

import commands

UPDATE_DOC_COMMAND = "cd /var/www/genro-docs; ./doc-update"
# 
# For testing:
# UPDATE_DOC_COMMAND = "date; sleep 10; date"

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def windowTitle(self):
        return '!!Update documentation'

    def main(self, rootBC, **kwargs):
        center, _top, _bottom = self.pbl_rootBorderContainer(rootBC, margin="1em", **kwargs)

        tb = center.contentPane(region="top").toolbar(_class="th_toolbar")
        buttons = tb.div(width="100%")
        buttons.div(_class='button_placeholder', float='left').button('!!Update documentation', fire="update_doc",
                                                                      visible="==(!_busy)", _busy="^busy")
        buttons.div("^busy")
        center.data('busy', '')

        center.contentPane(region="center", style="overflow: scroll").pre("^results_log")

        center.dataRpc('results_log', 'updateDocumentation', _fired="^update_doc",
                       _onCalling="SET busy = 'Updating documentation... Please wait.'", _onResult="SET busy = ''")

    def rpc_updateDocumentation(self, **kwargs):
        return commands.getoutput(UPDATE_DOC_COMMAND)