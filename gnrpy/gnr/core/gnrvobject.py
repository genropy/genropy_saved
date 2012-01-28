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

http://hypercontent.sourceforge.net/docs/manual/develop/vcard.html
http://vobject.skyhouseconsulting.com/epydoc/

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

VALID_VCARD_TAGS = ['n','fn','nickname','photo','bday','adr','label','tel','email',
              'mailer','tz','geo','title','role','logo','agent','org','note',
              'rev','sound','url','uid','version','key']

class VCard:
    def __init__(self, card=None,**kwargs):
        self.j=vobject.vCard()

        card=card or kwargs
        if card:
            self.fillFrom(card)


    def _tag_n(self,tag,data):
        if data:
            self.j.add('n')
            if data['family']: self.j.n.value.family=data['family']
            if data['given']: self.j.n.value.given=data['given']
            if data['additional']: self.j.n.value.additional=data['additional']
            if data['prefix']: self.j.n.value.prefix=data['prefix']
            if data['suffix']: self.j.n.value.suffix=data['suffix']

    def _tag_adr(self,tag,data):
        if data: # 'box', 'city', 'code', 'country', 'extended', 'lines', 'one_line', 'region', 'street'
            self.j.add('adr')
            if data['box']: self.j.adr.value.box=data['box']
            if data['city']: self.j.adr.value.city=data['city']
            if data['code']: self.j.adr.value.code=data['code']
            if data['country']: self.j.adr.value.country=data['country']
            if data['extended']: self.j.adr.value.extended=data['extended']
            if data['lines']: self.j.adr.value.lines=data['lines']
            if data['region']: self.j.adr.value.region=data['region']
            if data['street']: self.j.adr.value.street=data['street']


    def doserialize(self):
        return self.j.serialize()

    def doprettyprint(self):
        return self.j.prettyPrint()



    def setTag(self,tag,data):
        if data:
            print tag, data
            assert tag in VALID_VCARD_TAGS, 'ERROR: %s is not a valid tag' %tag
            if tag in ['n','adr']:
                getattr(self, '%s%s' %('_tag_',tag))(tag,data)
            else:
                count = 0
                for k2, v2 in data.items():
                    if v2:
                        path = '#%i' %count
                        count=count+1
                        m = self.j.add(tag)
                        setattr(m,'value',data[path])
                        if tag=='org':
                            m.isNative=False
                        attrlist = data['%s?param_list' %path]
                        if attrlist:
                            #for single_attr in attrlist:
                                #setattr(m,'%s_param' %single_attr,single_attr)
                                #setattr(m,'type_param',single_attr)
                            setattr(m,'type_paramlist',attrlist)


    def fillFrom(self,card):
        print 'card_bag'
        print card
        for tag,v in card.items():
            if tag=='n':
                self.setTag(tag,v)
            elif tag=='adr':
                self.setTag(tag,v)
            else:
                self.setTag(tag,v)


if __name__ == '__main__':

    x = Bag()
    x['n.family']='Smith'
    x['n.given']='Jeff'
    x['n.additional']='G.'
    x['fn.fn']='Jeff Smith'
    x['nickname.nickname']='Eddie'
    x['bday.bday']='1961-10-21'
    x['org.org']='Goodsoftware Pty Ltd'
    x.setItem('email.email','jeffsmith@me.com', param_list=['Home','type=INTERNET','type=pref'])
    x.addItem('email.email','jeffsmith@mac.com', param_list=['Work','type=INTERNET'])
    x['adr.street']='32 Smith Waters Rd'
    x['adr.city']='Kincumber'
    x['adr.code']='2251'
    x['adr.country']='Australia'
    x.setItem('tel.tel','02 4332 0368', param_list=['Home','type=pref'])
    x.addItem('tel.tel','0421 232 249', param_list=['CELL'])
    x.setItem('url.url','02 4332 0368', param_list=['Work'])
    

    c = VCard(x)
    print dir(c)
    print c.doserialize()
    #c.doprettyprint()