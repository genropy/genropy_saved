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

import ast
import os.path

from gnr.core.gnrbag import Bag
from gnr.devel.commands import command, argument

class DocAnalyzer(ast.NodeVisitor):
    """Reads a python source file and collects information about docstrings."""
    def __init__(self, filename):
        self.filename = filename
        with open(filename,'r') as fd:
            ast_tree = ast.parse(fd.read(), filename)
            self.current = self.module = Bag()
            self.module.setBackRef()
            self.module.label, _ = os.path.splitext(os.path.basename(filename))
            self.lineno = 0
            self.visit(ast_tree)

    def visit(self, node):
        """Visit nodes, gathering line numbers."""
        lineno = getattr(node, 'lineno', None)
        if lineno is not None and lineno > self.lineno:
            self.lineno = lineno
        super(DocAnalyzer, self).visit(node)
    
    def visit_ClassDef(self, node):
        """Visits 'class' nodes"""
        parent, self.current = self.current, Bag()
        start = self.lineno
        self.generic_visit(node)
        end = self.lineno
        parent.addItem(node.name, self.current, kind='class', docstring=ast.get_docstring(node), start=start, end=end)
        self.current = parent
    
    def visit_FunctionDef(self, node):
        """Visits 'def' nodes"""
        parent, self.current = self.current, Bag()
        start = self.lineno
        self.generic_visit(node)
        end = self.lineno
        parent.addItem(node.name, self.current, kind='def', docstring=ast.get_docstring(node), start=start, end=end)
        self.current = parent
    

@command('docblame', help="Check compliance to GenroPy documentation policy")
@argument('filenames', type=str, nargs='+', metavar="file.py", help="source file to check")
def main(filenames):
    """Check compliance to GenroPy documentation policy.
    
    It's our policy that when you change a class or method and it is missing a docstring,
    then you have to document it.
    
    Private methods (starting with '_') do not require documentation."""
    for fn in filenames:
        e = DocAnalyzer(fn)
        for node in e.module.traverse():
            if not node.label.startswith('_') and not node.getAttr('docstring'):
                print "%(file)s:%(line)d\t%(name)s (%(kind)s) missing docstring" % dict(file=fn, line=node.getAttr('start'), name=node.fullpath, kind=node.getAttr('kind'))

if __name__ == '__main__':
    main.run()