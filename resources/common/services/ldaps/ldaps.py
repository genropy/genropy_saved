#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#

# Required:
#
#    pip install python-ldap
#

from gnr.core.gnrstring import boolean
from gnr.lib.services.ldaps import LdapsService
from gnr.core.gnrdecorator import extract_kwargs
from ldap.controls import SimplePagedResultsControl
import ldap



class Main(LdapsService):
    """
    ldaps service (login, search and update AD data). 
    inside siteconfig.xml

        <services>
            ... other services

            <service_name                                   # Service's name, used in getService() metode.
                service_type='ldaps'                        # Service's type.
                resource='ldaps'                            # Resource's type.
                urlServer='ldap://IP_or_URL_SERVER LDAP'    # URL or IP to contact ldap server.
                baseDN='DC=example,DC=org'                  # Base of AD structure for search data.
                defaultDomain='AD domain'                   # explicit AD domain if server GENROPY are not in domain.
                userIdField='uid'                           # AD field used for identify user (default 'uid').
                userAttr=['attr to search']                 # Attributes for loged user to store.
                searchUser='user_for_serach'                # User to use for search in ldap server.
                searchPassword='password_for_search'        # Password for user used for search in ldap server.
                case='l'                                    # define if user is upper o lower case.
                getUserInfo='t/f'                           # default = y. 
            />
        </services>

    """

    @extract_kwargs(user=True)
    def __init__(self, parent=None, urlServer=None, baseDN=None, userIdField='uid', defaultDomain=None,
                loginTimeout=None,userDomainTemplate=None, userAttr=None,
                 searchUser=None, searchPassword=None, case=None, testMode=False,user_kwargs=None,getUserInfo='t',**kwargs):

        self.ldapClient = None
        self.parent = parent
        self.ldapServer = urlServer
        self.baseDN = baseDN
        self.userIdField = userIdField
        self.domain = defaultDomain
        self.userDomainTemplate = userDomainTemplate or '%(domain)s\\%(user)s'
        self.searchUser = searchUser
        self.searchPassword = searchPassword
        self.user_kwargs = user_kwargs
        self.userAttr = [str(x) for x in userAttr.split(',')] if userAttr else []
        self.case = case
        self.searchFilter = '(&(objectClass=person) (sAMAccountName=*) (objectClass=user))'
        self.loginTimeout = int(loginTimeout or 5)
        self.testMode = boolean(testMode)
        self.getUserInfo = boolean(getUserInfo)
        if not self.getUserInfo:
            self.user_kwargs = dict(username='username')
        if not self.ldapServer or not self.userIdField:
            raise ldap.SERVER_DOWN

    def __call__(self, user=None, password=None, **kwargs):
        """
            Calling from the default login form.
            :param user:        user to be logged
            :param password:    User passwords to be logged
            :return:            Return a proper dictionary with user data in the right format for logging in genropy, 
                                 dictionary key "ldap_user" is added that contains the output of the raw search from 
                                 LDAP server.
        """
        ldap_user = self.doLogin(user=user, password=password)
        if self.testMode:
            return ldap_user
        if not ldap_user:
            return False
        self.ldapClient.unbind()
        # make a response with genropy user data and ldap user data.
        externalUser = dict()
        for k, v in self.user_kwargs.items():
            externalUser[k] = ldap_user.get(v)

        externalUser['ldap_user'] = ldap_user
        return externalUser

    def doLogin(self, user=None, password=None, mode='Login', **kwargs):
        """
            Check your username and password credentials in the LDAP server
            :param user:        user to be logged
            :param password:    User passwords to be logged
            :param mode:        'Login' | 'Search' to select the type of data returned.
            :return:            If mode = 'Login' will return the user's default attributes. 
                                If mode = 'Search' is simply returned True for the verified user. 
                                Failure occurs, returns false for any mode.
        """

        if '\\' in user:
            self.domain, user = user.split('\\')
        elif '@' in user:
            user, self.domain = user.split('@')

        if not user:
            return False
        
        if self.testMode:
            return dict(username =user)
        if self.domain:
            user = self.userDomainTemplate %dict(domain=self.domain, user=user)
        if self.case == 'l':
            user = user.lower()
        elif self.case == 'u':
            user = user.upper()
        
        if not 'ldap://' in self.ldapServer:
            self.ldapServer = 'ldap://%s' % self.ldapServer
        try:
            self.ldapClient = ldap.initialize(self.ldapServer)
            self.ldapClient.set_option(ldap.OPT_REFERRALS, 0)
            self.ldapClient.simple_bind_s(user, password)
        except ldap.INVALID_CREDENTIALS:
            self.ldapClient.unbind()
            return False
        except ldap.SERVER_DOWN:
            return 'AD server not available'

        if mode == 'Login':
            if '\\' in user:
                username = user.split('\\')[1]
            elif '@' in user:
                username = user.split('@')[0]
            if self.getUserInfo:
                try:
                    user_attribute = self.ldapClient.search_s(self.baseDN, ldap.SCOPE_SUBTREE, '(%s=%s)' % (self.userIdField,
                                                            username), self.userAttr)[0][1]
                    for k, v in user_attribute.items():
                        user_attribute[k] = v[0] if isinstance(v, list) else v
                except ldap.LDAPError, e:
                    print e
            else:
                user_attribute = dict(username=username)
        elif mode == 'Search':
            user_attribute = True
        else:
            raise ldap.INVALID_SYNTAX

        return user_attribute

    def doSearch(self, searchFilter=None, retrieveAttributes=None):
        """
            Searches for records in an ldap server, Research is filtered and the result is a selection of individual 
            fields of the returned records.
            :param searchFilter:        It is the filter to search the LDAP server.
                                        The filter must be written in the LDAP filter format.
                                        If the filter is not specified, the default filter is used (defined in the 
                                         instance of the class).
                                        If the filter contains (@DefaultFilter) as a filter, the filter passed is added 
                                         to the default filter.
            :param retrieveAttributes:  This is the list of the attributes returned by the search for each record.
                                        The list of attributes is made up of a string with the list of attributes 
                                         separated by commas.
                                        If attributes are not specified, the default attributes (defined in the instance
                                         of the class are returned).
                                        If the list of attributes including @DefaultAttribute attribute, passed 
                                         attributes are added to the default attributes.
            :return:                    Return a list of dictionaries, a dictionary for each record. The value attached 
                                         to each key in turn is a list of strings. 
        """

        if searchFilter:
            if '(@DefaultFilter)' in searchFilter:
                searchFilter = '(' + self.searchFilter[1:-1] + searchFilter[1:-1].replace('(@DefaultFilter)', '') + ')'
        else:
            searchFilter = self.searchFilter

        if retrieveAttributes:
            retrieveAttributes = [str(attribute).strip() for attribute in retrieveAttributes.split(',')]
            if '@DefaultAttribute' in retrieveAttributes:
                retrieveAttributes = list(set(self.userAttr + retrieveAttributes))
                retrieveAttributes.remove('@DefaultAttribute')
        else:
            retrieveAttributes = self.userAttr

        page_size = 50
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        ldap.set_option(
					ldap.OPT_NETWORK_TIMEOUT,
					self.loginTimeout)
        req_ctrl = SimplePagedResultsControl(True, size=page_size, cookie='')

        ldap_user = self.doLogin(user=self.searchUser, password=self.searchPassword, mode='Search')

        if ldap_user:
            try:
                ldap_result_id = self.ldapClient.search_ext(self.baseDN, ldap.SCOPE_SUBTREE, searchFilter,
                                                            attrlist=retrieveAttributes,
                                                            serverctrls=[req_ctrl])

                result_set = []
                result_pages = 0
                while True:
                    rtype, rdata, rmsgid, rctrls = self.ldapClient.result3(ldap_result_id)

                    result_set.extend(rdata)
                    result_pages += 1
                    pctrls = [c for c in rctrls if c.controlType == SimplePagedResultsControl.controlType]
                    if pctrls:
                        if pctrls[0].cookie:
                            req_ctrl.cookie = pctrls[0].cookie
                            ldap_result_id = self.ldapClient.search_ext(self.baseDN, ldap.SCOPE_SUBTREE, searchFilter,
                                                                        attrlist=retrieveAttributes,
                                                                        serverctrls=[req_ctrl])
                        else:
                            break
            except ldap.LDAPError, e:
                print e
                return None
            finally:
                self.ldapClient.unbind_s()

            results = [record[1] for record in result_set]
            del results[-1]

            return results

        raise ldap.AUTH_UNKNOWN

    def getSchema(self):
        pass

    def insertRecord(self):
        pass

    def updateRecord(self):
        pass
