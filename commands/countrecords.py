#!/usr/bin/env python
# encoding: utf-8

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from gnr.core.gnrbag import Bag
from gnr.devel.commands import command, argument
from gnr.app.gnrapp import GnrApp

@command('countrecords', help="Count records in tables")
@argument('instance', type=GnrApp, metavar='instance', help="Istanza GenroPy")
@argument('packages', type=str, metavar="PACKAGE", help="Pacakges", nargs="*")
def main(instance, packages):
    if packages:
        iter_packages = (p for p in instance.db.packages.values() if p.name in packages)
    else:
        iter_packages = (p for p in instance.db.packages.values())
    for p in iter_packages:
        print "-"*60,"[",p.name,"]"
        for t in p.tables:
            tbl = instance.db.table("%s.%s" % (p.name, t))
            try:
                print "  %-40s : %d" % (t, tbl.query().count())
            except Exception, e:
                print "  %-40s : %s" % (t, str(e))

if __name__ == "__main__":
    main.run()
