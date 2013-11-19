#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  connection.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrlang import getUuid
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy

CONNECTION_TIMEOUT = 3600
CONNECTION_REFRESH = 20

USER_AGENT_SNIFF = (('Chrome', 'Chrome'),
                    ('Safari', 'Safari'),
                    ('Firefox', 'Firefox'),
                    ('Opera', 'Opera'),
                    ('MSIE', 'InternetExplorer'))

class GnrWebConnection(GnrBaseProxy):
    def init(self, connection_id=None, user=None, **kwargs):
        page = self.page
        self.user_agent = page.request.get_header('User-Agent') or ''
        self.browser_name = self.sniffUserAgent()
        self.ip = self.page.request.remote_addr or '0.0.0.0'
        self.connection_name = '%s_%s' % (self.ip.replace('.', '_'), self.browser_name)
        self.secret = page.site.config['secret'] or self.page.siteName
        self.cookie_name = self.page.siteName
        self.connection_id = None
        self.user = None
        self.user_tags = None
        self.user_id = None
        self.user_name = None
        self.cookie = self.read_cookie()
        self._cookie_data = None
        self.connection_item = None
        self.avatar_extra = dict()
        if connection_id:
            self.validate_connection(connection_id=connection_id, user=user)

        elif self.cookie:
            cv = self.cookie.value
            self.validate_connection(connection_id=cv.get('connection_id'), user=cv.get('user'))


    def create(self):
        self.connection_id = getUuid()
        self.user = self.guestname
        self.register()
        self.write_cookie()

    def validate_page_id(self, page_id):
        pages = self.connection_item.get('pages') or self.page.site.register.pages(connection_id=self.connection_item['register_item_id'])
        return page_id in pages

    def validate_connection(self, connection_id=None, user=None):
        connection_item = self.page.site.register.connection(connection_id)
        if connection_item:
            if (connection_item['user'] == user) and (connection_item['user_ip'] == self.page.request.remote_addr):
                self.connection_id = connection_id
                self.user = user
                self.user_tags = connection_item['user_tags']
                self.user_id = connection_item['user_id']
                self.user_name = connection_item['user_name']
                self.avatar_extra = connection_item.get('avatar_extra')
                self.connection_item = connection_item

    @property
    def guestname(self):
        """TODO"""
        return 'guest_%s' % self.connection_id

    def register(self):
        return self.page.site.register.new_connection(self.connection_id, self)

    def unregister(self):
        self.page.site.register.drop_connection(self.connection_id)

    def upd_registration(self, user):
        pass

    def read_cookie(self):
        return self.page.get_cookie(self.cookie_name, 'marshal', secret=self.secret)

    def write_cookie(self):
        self.cookie = self.page.newMarshalCookie(self.cookie_name, {'user': self.user,
                                                                    'connection_id': self.connection_id,
                                                                    'data': self.cookie_data,
                                                                    'locale': None}, secret=self.secret)
        self.cookie.path = self.page.site.default_uri
        self.page.add_cookie(self.cookie)

    @property
    def loggedUser(self):
        """TODO"""
        return (self.user != self.guestname) and self.user

    @property
    def cookie_data(self):
        """TODO"""
        if self._cookie_data is None:
            if self.cookie:
                self._cookie_data = self.cookie.value.get('data') or {}
            else:
                self._cookie_data = {}
        return self._cookie_data


    def sniffUserAgent(self):
        user_agent = self.user_agent
        for k, v in USER_AGENT_SNIFF:
            if k in  user_agent:
                return v
        return 'unknown browser'

    def _get_locale(self):
        if self.cookie:
            return self.cookie.value.get('locale')

    def _set_locale(self, v):
        self.cookie.value['locale'] = v

    locale = property(_get_locale, _set_locale)

    def change_user(self, avatar=None):
        avatar_dict = avatar.as_dict() if avatar else dict()
        self.user = avatar_dict.get('user') or self.guestname
        self.user_tags = avatar_dict.get('user_tags')
        self.user_name = avatar_dict.get('user_name')
        self.user_id = avatar_dict.get('user_id')
        if avatar:
            self.avatar_extra = avatar.extra_kwargs

        self.page.site.register.change_connection_user(self.connection_id, user=self.user,
                                                       user_tags=self.user_tags, user_id=self.user_id,
                                                       user_name=self.user_name, avatar_extra=self.avatar_extra)
        self.write_cookie()

    def rpc_logout(self):
        self.page.site.register.drop_user(user=self.user)

    @public_method
    def connected_users_bag(self, exclude=None, exclude_guest=True, max_age=600):
        users = self.page.site.register.users()
        result = Bag()
        exclude = exclude or []
        now = self.page.clientDatetime()
        if isinstance(exclude, basestring):
            exclude = exclude.split(',')
        for user, arguments in users.items():
            if user in exclude:
                continue
            row = dict()
            if exclude_guest and user.startswith('guest_') or user == self.page.user:
                continue
            _customClasses = []
            row['_pkey'] = user
            row['iconClass'] = 'greenLight'
            last_refresh_age = (now - arguments.get('last_refresh_ts',arguments['start_ts'])).seconds
            last_event_age = (now - arguments.get('last_user_ts',arguments['start_ts'])).seconds
            if last_refresh_age > 60:
                _customClasses.append('user_disconnected')
                row['iconClass'] = 'grayLight'
            elif last_event_age>300:
                _customClasses.append('user_away')
                row['iconClass'] = 'redLight'
            elif last_event_age > 60:
                _customClasses.append('user_idle')
                row['iconClass'] = 'yellowLight'
            row['_customClasses'] = _customClasses
            row['caption'] = arguments['user_name'] or user
            row.update(arguments)
            row.pop('datachanges', None)
            result.setItem(user, None, **row)
        return result



        
