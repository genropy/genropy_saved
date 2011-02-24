# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrmail : gnr mail controller
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
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

import smtplib

from email.MIMEText import MIMEText

def sendmail(host, from_address, to_address, subject, body, user='', password=''):
    """add???
    
    :param host: add???
    :param from_address: add???
    :param to_address: add???
    :param subject: add???
    :param body: add???
    :param user: add???. Default value is ``''``
    :param password: add???. Default value is ``''``
    """
    msg = MIMEText(body)
    
    if isinstance(to_address, basestring):
        to_address = [k.strip() for k in to_address.split(',')]
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = ','.join(to_address)
    
    s = smtplib.SMTP(host=host)
    if user:
        s.login(user, password)
    s.sendmail(from_address, to_address, msg.as_string())
    s.close()