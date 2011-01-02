#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 

MSG_DEFAULT_EXPIRY = 10
from datetime import datetime
from gnr.core.gnrlist import sortByItem

class GnrMessageHandler(object):
    """
    Message handler that uses gnrshareddata.
    There are 3 types of message:
    U-user       :Messages for an user
    C-connection :Messages for one connection
    P-page       :Messages for one page
    Any message is posted at a specific address composed by the prefix
    'MSG', the message type, the destination and a counter.For instance :
    MSG-U-jbrown-5 is the message n.5 for the user jbrown.
    MSG-P-cXhSPJ0BMfGs0vCBSk7Fag-34 is trhe message 34 for a page.
    For any possible address there are also 2 locations used to store
    messages written and read.
    So we will have also for instance the location MSG-U-jbrown-W and
    MSG-U-jbrown-R that are the counters for jbrown messages.
    When a message is posted it is written in the shareddata and the 
    counter is incremented.
    Any message has an expiry time and a body.
    
    """

    def __init__(self, site):
        self.site = site
        self.sd = self.site.shared_data

    def _buildMessageEnvelope(self, body=None, message_type=None, src_page_id=None, src_user=None,
                              src_connection_id=None, **kwargs):
        return dict(body=body, message_type=message_type, src_page_id=src_page_id, src_user=src_user,
                    src_connection_id=src_connection_id, msg_ts=datetime.now(), **kwargs)

    def _postMessage(self, dest_type, address, body, expiry, message_type=None, src_page_id=None, src_user=None,
                     src_connection_id=None, **kwargs):
        sd = self.site.shared_data
        address = 'MSG-%s-%s' % (dest_type, address)
        message = self._buildMessageEnvelope(body=body, message_type=message_type,
                                             src_connection_id=src_connection_id,
                                             src_user=src_user, src_page_id=src_page_id, **kwargs)
        with sd.locked(key=address):
            counter_w = '%s_W' % address
            k = sd.incr(counter_w)
            if k is None:
                k = 1
                sd.set(counter_w, k)
            key = '%s_%i' % (address, k)
            sd.set(key, message, expiry)

    def _getMessages(self, dest_type, address):
        sd = self.site.shared_data
        address = 'MSG-%s-%s' % (dest_type, address)
        result = []
        with sd.locked(key=address):
            cnt = sd.get_multi(['R', 'W'], '%s_' % address)
            r_msg = cnt.get('R', 0)
            w_msg = cnt.get('W', 0)
            if w_msg > r_msg:
                messages = sd.get_multi([str(k + 1) for k in range(r_msg, w_msg)], '%s_' % address)
                result = [messages[str(k + 1)] for k in range(r_msg, w_msg) if str(k + 1) in messages]
                sd.set('%s_R' % address, w_msg)
        return result

    def postPageMessage(self, page_id, body, expiry=MSG_DEFAULT_EXPIRY, message_type=None, src_page_id=None,
                        src_user=None, src_connection_id=None, **kwargs):
        return self._postMessage('P', page_id, body, expiry=expiry, message_type=message_type, src_page_id=src_page_id,
                                 src_user=src_user, src_connection_id=src_connection_id, **kwargs)

    def postUserMessage(self, username, body, expiry=MSG_DEFAULT_EXPIRY, message_type=None, src_page_id=None,
                        src_user=None, src_connection_id=None, **kwargs):
        return self._postMessage('U', username, body, expiry=expiry, message_type=message_type, src_page_id=src_page_id,
                                 src_user=src_user, src_connection_id=src_connection_id, **kwargs)

    def postConnectionMessage(self, connection_id, body, expiry=MSG_DEFAULT_EXPIRY, message_type=None, src_page_id=None,
                              src_user=None, src_connection_id=None, **kwargs):
        return self._postMessage('C', connection_id, body, expiry=expiry, message_type=message_type,
                                 src_page_id=src_page_id, src_user=src_user, src_connection_id=src_connection_id,
                                 **kwargs)

    def getPageMessages(self, page_id):
        return self._getMessages('P', page_id)

    def getUserMessages(self, username):
        return self._getMessages('U', username)

    def getConnectionMessages(self, connection_id):
        return self._getMessages('C', connection_id)

    def getMessages(self, page_id=None, connection_id=None, user=None):
        messages = []
        if page_id:
            messages.extend(self.getPageMessages(page_id))
        if connection_id:
            messages.extend(self.getConnectionMessages(connection_id))
        if user:
            messages.extend(self.getUserMessages(user))
        return sortByItem(messages, 'msg_ts')
        
