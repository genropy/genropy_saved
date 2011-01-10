#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

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

from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy

class GnrBaseFrontend(GnrBaseProxy):
    """Base class for GnrWebPage frontends.
    
    Frontends define the details to load different UI toolkits (e.g. different versions of Dojo).
    """

    def init(self, **kwargs):
        """Initialize this frontend."""
        pass

    def importer(self):
        """Returns the HTML code used to load any client-side resource (e.g. a specific dojo library) specific to this frontend."""
        return ''

    def event_onBegin(self):
        pass

    def frontend_arg_dict(self):
        """Parameters to be passed to the page template."""
        return 