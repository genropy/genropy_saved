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

"""
A framework to build command line utilities in GenroPy.

Argument parsing inspired by Michele Simionato's plac.

::

    Three scripts for the genro-kings under softwell sky,
    Seven for goodsoftware-lords in their halls of stone,
    Nine for mortal customers with money they will buy,
    One for the Dark Lord Gio on his dark throne,
    In the Land of GenroPy where the Commands lie.
    One Script to rule them all, One Script to find them,
    One Script to bring them all and in the darkness bind them
    In the Land of GenroPy where the Commands lie.
"""

import sys
import os.path
import argparse
import inspect
import imp

from gnr.devel.utils import AutoDiscovery

# --------------------------------------------------------------------------------------------- Globals

command_registry = {}

# --------------------------------------------------------------------------------------------- Constants

_COMMAND_ARGUMENTS = "__gnrcmd__arguments__"

def command(name=None, description=None, *args, **kwargs):
    """A decorator to define new 'gnr' commands.
    
    See ``ArgumentParser`` constructor in the ``argparse`` module for help on args."""
    def decorator(cmd):
        global command_registry
        if command_registry.get(name, None) is not None:
            raise KeyError, "Command '%(name)s' already defined in %(file)s" % dict(name=name,file=command_registry['name'].__file__)
        desc = description if description else cmd.__doc__
        cmd = GnrCommand(main=cmd, name=name or cmd.__name__.lower(), description=desc, *args, **kwargs)
        command_registry[name] = cmd
        return cmd
    return decorator

def argument(dest, *args, **kwargs):
    """A decorator to describe arguments to a 'gnr' command.
    
    See ``add_argument`` in the ``argparse`` module for help on args."""
    args = list(args)
    def decorator(cmd):
        argspec = vars(cmd).setdefault(_COMMAND_ARGUMENTS, {})
        func_args, _, _, func_defaults = inspect.getargspec(cmd)
        if not func_defaults:
            func_defaults = ()
        try:
            default = func_defaults[func_args.index(dest) - (len(func_args) - len(func_defaults))]
            has_default = True
        except IndexError:
            has_default = False
            
        if not args:
            if has_default:
                args.append('--%s' % dest)
                kwargs['dest'] = dest
            else:
                args.append(dest)

        # some magic for special cases
        if has_default:
            if default is True:
                kwargs['action'] = 'store_false'
                kwargs['default'] = True
        
            if default is False:
                kwargs['action'] = 'store_true'
                kwargs['default'] = False
            
            kwargs['help'] = "%s (default: %s)" % (kwargs.get('help',''), repr(default))
        
        argspec[dest] = (args, kwargs)
        return cmd
    return decorator

class GnrCommand(object):
    """A command line utility."""
    def __init__(self, main=None, name=None, help=None, *args, **kwargs):
        super(GnrCommand, self).__init__()
        self.name = name
        self.help = help
        self.parser_args = args
        self.parser_kwargs = kwargs
        self.main = main
    
    @property
    def filename(self):
        """File where main is implemented"""
        try:
            return self.main.func_code.co_filename
        except:
            return "(unknown)"
    
    @property
    def lineno(self):
        """Line where main is implemented"""
        try:
            return self.main.func_code.co_firstlineno
        except:
            return "(unknown)"
    
    @property
    def description(self):
        """Returns the command description"""
        return self.parser_kwargs.get('description','')
    
    def run(self, *args, **kwargs):
        """Run this command."""
        parser = self.init_parser()
        if kwargs:
            parser.set_defaults(**kwargs)
        arguments = parser.parse_args(args or None)
        return self.main(**vars(arguments))
    
    def main(self):
        raise NotImplementedError("Do not use GnrCommand directly, apply @command to a callable.")
    
    def __call__(self, *args, **kwargs):
        return self.main(*args, **kwargs)
    
    def init_parser(self, subparsers=None):
        """Initialize this command's arguments."""
        if not subparsers:
            parser = argparse.ArgumentParser(*self.parser_args, **self.parser_kwargs)
        else:
            parser = subparsers.add_parser(self.name, help=self.help, *self.parser_args, **self.parser_kwargs)
            parser.set_defaults(main=self.main)
        arguments = self.auto_arguments()
        custom_arguments = getattr(self.main, _COMMAND_ARGUMENTS, {})
        arguments.update(custom_arguments)
        func_args, _, _, _ = inspect.getargspec(self.main)
        for name in func_args:     
            args, kwargs = arguments[name]
            parser.add_argument(*args, **kwargs)
        return parser
    
    def auto_arguments(self):
        """Auto-generate a standard argument configuration from __call__'s python arguments"""
        args, _, _, defaults = inspect.getargspec(self.main)
        if not defaults:
            defaults = ()
        required = args[:len(args)-len(defaults)]
        optional = args[len(args)-len(defaults):]
        
        auto = {}
        for name in required:
            auto[name] = ((name,), {}) # arguments for add_argument

        for name, default in zip(optional, defaults):
            arg_type = type(default)
            kwargs = dict(dest=name, type=arg_type, default=default, help="(default: %s)" % repr(default))
            if arg_type is bool:
                kwargs['action'] = 'store_false' if (default == True) else 'store_true'
                del kwargs['type']
            elif arg_type is type: # a class
                arg_type = default.__class__
                kwargs['type'] = arg_type
                kwargs['metavar'] = arg_type.__name__
            auto[name] = (("--%s" % name,), kwargs)
        return auto

class CmdRunner(object):
    """Runs GenroPy commands.
    
    This class implements the 'gnr' command.
    """
    def __init__(self):
        self._discover_commands()
    
    def _discover_commands(self):        
        sys.modules['gnr.commands'] = imp.new_module('gnr.commands')
        
        ad = AutoDiscovery()
        for name, cmd in ad.all_commands.items():
            imp.load_source('gnr.commands.%s' % name, cmd.path)
    
    def main(self):
        """Parse command line and execute 'gnr' commands."""
        parser = self.setup_parser()
        args = parser.parse_args()
        assert args.main, "No command specified"
        main = args.main
        del args.main
        main(**vars(args))
    
    def setup_parser(self):
        global command_registry
        parser = argparse.ArgumentParser(description="Run Genro commands")
        subparsers = parser.add_subparsers(title="commands")
        for cmd in command_registry.values():
            cmd.init_parser(subparsers)
        return parser

@command('commands', help="List commands and where they are implemented")
@argument('verbose', '-v','--verbose', help="Show command description")
def commands(verbose=False):
    global command_registry
    for name, cmd in command_registry.items():
        print "%(name)-20s %(filename)s:%(lineno)s" % dict(name=name, filename=cmd.filename, lineno=cmd.lineno)
        if verbose and cmd.help:
            print "%(space)20s %(help)s" % dict(space=" ", help=cmd.help)

@command('adreport', help="Print AutoDiscovery report")
@argument('full', '-f','--full', help="Show full report")
def info(full=False):
    ad = AutoDiscovery()
    ad.report(full)

@command('adenv', help="Print current project/instance/package/site as environment variables")
@argument('dirs','-d','--dirs', help="print directories too")
def info(dirs=False):
    ad = AutoDiscovery()
    print "CURRENT_PROJECT=%s" % (ad.current_project.name if ad.current_project else '')
    print "CURRENT_INSTANCE=%s" % (ad.current_instance.name if ad.current_instance else '')
    print "CURRENT_PACKAGE=%s" % (ad.current_package.name if ad.current_package else '')
    print "CURRENT_SITE=%s" % (ad.current_site.name if ad.current_site else '')
    if dirs:
        print "CURRENT_PROJECT_DIR=%s" % (ad.current_project.path if ad.current_project else '')
        print "CURRENT_INSTANCE_DIR=%s" % (ad.current_instance.path if ad.current_instance else '')
        print "CURRENT_PACKAGE_DIR=%s" % (ad.current_package.path if ad.current_package else '')
        print "CURRENT_SITE_DIR=%s" % (ad.current_site.path if ad.current_site else '')    