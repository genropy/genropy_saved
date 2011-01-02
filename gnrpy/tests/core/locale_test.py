# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# test locale   : test for locale 
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




import datetime
import pytz
from gnr.core.gnrlocale import localize, parselocal
from decimal import Decimal

class TestLocalize:
    def setup_class(cls):
        cls.date = datetime.date(2007, 12, 10)
        cls.datetime = datetime.datetime(2007, 12, 10, 22, 15, 36)
        cls.time = datetime.time(12, 23, 44, 59400)
        cls.perc = 0.3256
        cls.tz = pytz.timezone('Europe/Berlin')

    def test_noformat_int(self):
        assert localize(125) == '125'
        assert localize(125, locale='it_IT') == '125'

    def test_noformat_float(self):
        assert localize(12.445) == '12.445'
        assert localize(125.445, locale='it_IT') == '125,445'

    def test_noformat_decimal(self):
        x = Decimal("1239988655.45111665677")
        assert localize(x) == '1,239,988,655.451'
        assert localize(x, locale='it_IT') == '1.239.988.655,451'

    def test_format_int_positive(self):
        assert localize(12567, '00000000') == '00012567'
        assert localize(12567, '#;(#)') == '12567'
        assert localize(1256789, "#,##0;(#)") == '1,256,789'

    def test_format_int_zero(self):
        assert localize(0, '######;(#)') == '0'
        assert localize(0, '#####0;(#);-*-') == '-*-'

    def test_format_int_negative(self):
        assert localize(-12567, '00000000;-0') == '-00012567'
        assert localize(-12567, '00000000;0 -') == '00012567 -'
        assert localize(-12567, '00000000;(#)') == '(00012567)'

    def test_format_int_special(self):
        assert localize(125, 'CR 0;DB 0; NoChange') == 'CR 125'
        assert localize(-125, 'CR 0;DB 0; NoChange') == 'DB 125'
        assert localize(0, 'CR 0;DB 0;No Change') == 'No Change'

    def test_format_float(self):
        assert localize(14.234) == '14.234'
        assert localize(125.34, '000000') == '000125'
        assert localize(125.44, '000000;(0)') == '000125'
        assert localize(-125, '000000;(-0)') == '(-000125)'
        assert localize(0, '000000;(0)') == '000000'
        assert localize(0, '000000;(0);--') == '--'
        assert localize(125, 'CR 0;DB 0; NoChange') == 'CR 125'
        assert localize(-125, 'CR 0;DB 0; NoChange') == 'DB 125'
        assert localize(0, 'CR 0;DB 0;No Change') == 'No Change'

    def test_format_dec_positive(self):
        x = Decimal("1239988655.45611665677")
        assert localize(x, '#.0') == '1239988655.4'
        assert localize(x, '#.0', locale='it_IT') == '1239988655,4'
        assert localize(x, '#.#') == '1239988655.4'
        assert localize(x, '#.#', locale='it_IT') == '1239988655,4'
        assert localize(x, '#.#####') == '1239988655.45612'
        assert localize(x, '#.#####', locale='it_IT') == '1239988655,45612'
        assert localize(x, '#,###.#####') == '1,239,988,655.45612'
        assert localize(x, '#,###.#####', locale='it_IT') == '1.239.988.655,45612'

    def test_format_dec_negative(self):
        x = Decimal("-1239988655.45611665677")
        assert localize(x, '#.0') == '-1239988655.4'
        assert localize(x, '#.0;(#)', locale='it_IT') == '(1239988655,4)'
        assert localize(x, '#.#;-  #') == '-  1239988655.4'
        assert localize(x, '#.#;DB #', locale='it_IT') == 'DB 1239988655,4'

    def test_format_currency(self):
        x = Decimal("1239988655.45611665677")
        assert localize(x, u'¤ #.0', u'EUR') == u'€ 1239988655.4'
        assert localize(x, u'¤ #.0', u'$') == u'$ 1239988655.4'
        assert localize(x, u'Please pay #.#### ¤ ASAP', u'EUR', locale='it_IT') == u'Please pay 1239988655,4561 € ASAP'

    def test_date(self):
        assert localize(self.date) == '12/10/07'

    def test_dateLocale(self):
        assert localize(self.date, locale='en') == '12/10/07'
        assert localize(self.date, locale='it') == '10/12/07'
        assert localize(self.date, locale='de') == '10.12.07'

    def test_dateLocaleShort(self):
        assert localize(self.date, locale='en') == '12/10/07'
        assert localize(self.date, locale='it') == '10/12/07'
        assert localize(self.date, locale='de') == '10.12.07'

    def test_dateLocaleMedium(self):
        assert localize(self.date, locale='en', format='medium') == 'Dec 10, 2007'
        assert localize(self.date, locale='it', format='medium') == '10/dic/2007'
        assert localize(self.date, locale='de', format='medium') == '10.12.2007'

    def test_dateLocaleLong(self):
        assert localize(self.date, locale='en', format='long') == 'December 10, 2007'
        assert localize(self.date, locale='it', format='long') == '10 dicembre 2007'
        assert localize(self.date, locale='de', format='long') == '10. Dezember 2007'

    def test_dateLocaleFull(self):
        assert localize(self.date, locale='en', format='full') == 'Monday, December 10, 2007'
        assert localize(self.date, locale='it', format='full') == u'lunedì 10 dicembre 2007'
        assert localize(self.date, locale='de', format='full') == 'Montag, 10. Dezember 2007'

    def test_dateLocaleFormat(self):
        assert localize(self.date, locale='en', format="EEE MMM d 'year:'yy") == 'Mon Dec 10 year:07'
        assert localize(self.date, locale='it', format="EEE MMM d 'anno:'yy") == "lun dic 10 anno:07"
        assert localize(self.date, locale='it', format='EEEE d MMMM yyyyG') == u'lunedì 10 dicembre 2007dC'
        assert localize(self.date, locale='de', format='EEEE d MMMM yyyyG') == u'Montag 10 Dezember 2007n. Chr.'
        assert localize(self.date, locale='en', format='D yyyyG') == '344 2007AD'
        assert localize(self.date, locale='en', format='ee LLLLL yyyyG') == '01 D 2007AD'


    def test_datetimeLocale(self):
        assert localize(self.datetime, locale='en', format='short') == '12/10/07 10:15 PM'
        assert localize(self.datetime, locale='it', format='short') == '10/12/07 22.15'
        assert localize(self.datetime, locale='de', format='short') == '10.12.07 22:15'

        assert localize(self.datetime, locale='en', format='medium') == 'Dec 10, 2007 10:15:36 PM'
        assert localize(self.datetime, locale='it', format='medium') == '10/dic/2007 22.15.36'
        assert localize(self.datetime, locale='de', format='medium') == '10.12.2007 22:15:36'

        assert localize(self.datetime, locale='en', format='long') == 'December 10, 2007 10:15:36 PM +0000'
        assert localize(self.datetime, locale='it', format='long') == '10 dicembre 2007 22.15.36 +0000'
        assert localize(self.datetime, locale='de', format='long') == '10. Dezember 2007 22:15:36 +0000'

        assert localize(self.datetime, locale='en',
                        format='full') == 'Monday, December 10, 2007 10:15:36 PM World (GMT) Time'
        assert localize(self.datetime, locale='it', format='full') == u'lunedì 10 dicembre 2007 22.15.36 Mondo (GMT)'
        assert localize(self.datetime, locale='de', format='full') == u'Montag, 10. Dezember 2007 22:15:36 Welt (GMT)'


    def test_timeLocale(self):
        assert localize(self.time, locale='en', format='short') == '12:23 PM'
        assert localize(self.time, locale='it', format='short') == '12.23'
        assert localize(self.time, locale='de', format='short') == '12:23'

        assert localize(self.time, locale='en', format='medium') == '12:23:44 PM'
        assert localize(self.time, locale='it', format='medium') == '12.23.44'
        assert localize(self.time, locale='de', format='medium') == '12:23:44'

        assert localize(self.time, locale='en', format='long') == '12:23:44 PM +0000'
        assert localize(self.time, locale='it', format='long') == '12.23.44 +0000'
        assert localize(self.time, locale='de', format='long') == '12:23:44 +0000'

    def test_timeLocaleFormat(self):
        assert localize(self.time, locale='en', format='a h:m:s--A') == 'PM 12:23:44--44624059'

    def test_none(self):
        assert localize(None) == ''
        assert localize(None, locale='de') == ''
        assert localize(None, locale='it') == ''

    def test_parse_number(self):
        assert parselocal('2', int, locale='it') == 2
        assert parselocal('1,990', int) == 1990
        assert parselocal('1.990', int, locale='it') == 1990

    def test_parse_float(self):
        assert parselocal('2,56', float, locale='it') == 2.56
        assert parselocal('1.990', float) == 1.99
        assert parselocal('1,990', float, locale='it') == 1.99

    def test_parse_decimal(self):
        assert parselocal('22.344.512.342.334,567765612', Decimal, locale='it') == Decimal("22344512342334.567765612")
        assert parselocal('22,344,512,342.334567765612', Decimal, locale='en') == Decimal("22344512342.334567765612")
        assert parselocal('22.344.512.342,334567765612', Decimal, locale='it') == Decimal("22344512342.334567765612")


    def test_parse_dateLocale(self):
        assert parselocal('10/12/07', datetime.date, locale='it') == self.date
        assert parselocal('12/10/07', datetime.date, locale='en') == self.date
        assert parselocal('10/12/2007', datetime.date, locale='it') == self.date
        assert parselocal('12/10/2007', datetime.date, locale='en') == self.date
        assert parselocal('10-12-07', datetime.date, locale='it') == self.date
        assert parselocal('12 10 07', datetime.date, locale='en') == self.date
        assert parselocal('10.12.2007', datetime.date, locale='it') == self.date

    def test_parse_datetimeLocale(self):
        #not implemented
        pass
        #assert parselocal('10/12/07', datetime.datetime, locale='it') == self.datetime
        #assert parselocal('12/10/07 10:15 PM', datetime.date, locale='en') == self.datetime

    def test_parse_time(self):
        assert parselocal('12:23:44 PM', datetime.time, locale='en') == datetime.time(12, 23, 44)
        

