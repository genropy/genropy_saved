# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrbag : an advanced data storage system
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Jeff Edwards
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

"""
The gnrvObject module contains two classes for dealing with vCard and vCal objects.

Name    Description Semantic
N           Name            A structured representation of the name of the person, place or thing associated with the vCard object.
FN          Formatted Name  The formatted name string associated with the vCard object
NICKNAME    Nickname        A descriptive or familiar name given instead of or in addition to the one belonging to a person, place, or thing.
PHOTO       Photograph      An image or photograph of the individual associated with the vCard
BDAY        Birthday        Date of birth of the individual associated with the vCard
ADR         Delivery Address A structured representation of the physical delivery address for the vCard object
LABEL       Label Address   Addressing label for physical delivery to the person/object associated with the vCard
TEL         Telephone       The canonical number string for a telephone number for telephony communication with the vCard object
EMAIL       Email           The address for electronic mail communication with the vCard object
MAILER      Email Program (Optional)    Type of email program used
TZ          Time Zone       Information related to the standard time zone of the vCard object
GEO         Global Positioning  The property specifies a latitude and longitude
TITLE       Title           Specifies the job title, functional position or function of the individual associated with the vCard object within an organization (V. P. Research and Development)
ROLE        Role or occupation  The role, occupation, or business category of the vCard object within an organization (e.g. Executive)
LOGO        Logo            An image or graphic of the logo of the organization that is associated with the individual to which the vCard belongs
AGENT       Agent           Information about another person who will act on behalf of the vCard object. Typically this would be an area administrator, assistant, or secretary for the individual
ORG         Organization Name or Organizational unit    The name and optionally the unit(s) of the organization associated with the vCard object. This property is based on the X.520 Organization Name attribute and the X.520 Organization Unit attribute
NOTE        Note            Specifies supplemental information or a comment that is associated with the vCard
REV         Last Revision   Combination of the calendar date and time of day of the last update to the vCard object
SOUND       Sound           By default, if this property is not grouped with other properties it specifies the pronunciation of the Formatted Name property of the vCard object.
URL         URL             A URL is a representation of an Internet location that can be used to obtain real-time information about the object to which the vCard refers. For example, a personal website or the company's web portal.
UID         Unique Identifier   Specifies a value that represents a persistent, globally unique identifier associated with the object
VERSION     Version Version of the vCard Specification
KEY         Public Key  The public encryption key associated with the vCard object
"""

from gnr.core.gnrbag import Bag
import os.path
import sys
import vobject

class vCard:
    def __init__(self, card=None,**kwargs):
        self.j=vobject.vCard()

        card=card or kwargs
        if card:
            self.fillFrom(card)

    def _tag_n(self,data):
        self.j.add('n')
        self.j.n.value = vobject.vcard.Name( family=data['family'], given=data['given'],additional=data['additional'] )

    def _tag_fn(self,data):
        self.j.add('fn')
        self.j.fn.value =data

    def _tag_email(self,data):
        self.j.add('email')
        self.j.email.value = data
        self.j.email.type_param = 'INTERNET'

    def _tag_nickname(self,data):
        self.j.add('nickname')
        self.j.nickname.value = data

    def _tag_bday(self,data):
        self.j.add('bday')
        self.j.bday.value = data

    def _tag_adr(self,data):
        self.j.add('adr')
        self.j.adr.value = data


    def _serialize(self):
        self.j.serialize()

    def _prettyprint(self):
        self.j.prettyPrint()

    def SetItem(self,tag,data):
        if not tag[0]=='_':
            tag = '%s%s' %('_tag_',tag)
        methodToCall = getattr(self, tag)
        methodToCall(data)

    def fillFrom(self,card):
        if 'name_first' in card and 'name_last' in card and 'name_second' in card:
            self.SetItem('n',dict(family=card['name_first'], given=card['name_last'],additional=card['name_second'] ))
            self.SetItem('fn','%s %s' %(card['name_first'],card['name_last']))
        elif 'name_first' in card and 'name_last' in card:
            self.SetItem('n',dict(family=card['name_first'], given=card['name_last']))
            self.SetItem('fn','%s %s' %(card['name_first'],card['name_last']))
        elif 'name_last' in card:
            self.SetItem('n',dict(given=card['name_last']))
            self.SetItem('fn',card['name_last'])
        elif 'name_first' in card:
            self.SetItem('n',dict(given=card['name_first']))
            self.SetItem('fn',card['name_first'])

        if 'email' in card: self.SetItem('email',card['email'])
        if 'name_preferred' in card: self.SetItem('nickname',card['name_preferred'])
        if 'dob' in card: self.SetItem('bday',card['dob'])
        # >>> card.adr.value == vobject.vcard.Address(u'5\u1234 Nowhere, Apt 1', 'Berkeley', 'CA', '94704', 'USA')
        #self._tag_adr(data)
        self._serialize()
        self.j.prettyPrint()

if __name__ == '__main__':
    
    card_rec=dict(name_first='Jeff',
                  name_last='Edwards',
                  name_second='B.',
                  name_preferred='Eddie',
                  email='jeffedwa@me.com')
    c = vCard(card_rec)