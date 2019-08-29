# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrtimestamp : timestamp utility class
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
# --------------------------------------------------------------------------
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from __future__ import division
from __future__ import print_function
from builtins import range
#from builtins import object
from past.utils import old_div
import datetime
from gnr.core import gnrstring

BASE36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class GnrTimeStamp(object):
    def __init__(self):
        self.startdate = datetime.datetime(1990, 1, 1)
        self.lastSec = 0
        self.lastCount = 0

    def get(self, station=1, base=1):
        maxcount = int(old_div(800000, base) + 0.999)
        while True:
            delta = datetime.datetime.now() - self.startdate
            if(delta.seconds != self.lastSec):
                self.lastSec = delta.seconds
                self.lastCount = 1
                if base == 1: self.lastCount = self.lastCount + delta.microseconds % 100
            else:
                self.lastCount = self.lastCount + 1
            counter = self.lastCount + ((station - 1) * maxcount)
            if self.lastCount < maxcount: break

        return ''.join(
                self.encode(delta.days - 1, 3) + self.encode(delta.seconds * 18 + old_div(counter, 46000), 4) + self.encode(
                        counter % 46000, 3))

    def encode(self, number, nChars):
        b = len(BASE36)
        result = []
        while (number >= 1):
            result.insert(0, BASE36[(number % b)])
            number = old_div(number, b)

        if (len(result) > nChars): result = []
        elif (len(result) < nChars):
            for x in range(nChars - len(result)):
                result.insert(0, BASE36[0])
        return ''.join(result)
    
    def getDate(self,gnrts):
        return self.startdate+datetime.timedelta(days=BASE36.index(gnrts[0])*36**2+BASE36.index(gnrts[1])*36+BASE36.index(gnrts[2]))

if __name__ == '__main__':
    s = GnrTimeStamp()
    print(s.get(station=1, base=100))
    print(s.get(station=1, base=100))
    print(s.get(station=1, base=100))
    print(s.get(station=1, base=100))
    print(s.get(station=2, base=100))
    print(s.get(station=3, base=100))
    print(s.get(station=1, base=100))
    print(s.get(station=2, base=100))
    print(s.get(station=3, base=100))
    print(s.get())
    print(s.getDate(s.get()))

	
