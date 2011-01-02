#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool
import twitter

class Twitter(BaseWebtool):
    def __call__(self, username=None, password=None, status=None):
        twitter_api = twitter.Api(username=username, password=password)
        self.content_type = 'application/text'
        twitter_status = twitter_api.PostUpdate(status)
        return twitter_status.text
        