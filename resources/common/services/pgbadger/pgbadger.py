#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from subprocess import call
from gnr.core.gnrlang import getUuid

import os


class Main(GnrBaseService):
    def __init__(self, parent=None,logfile=None,format=None,log_line_prefix=None,output_folder=None,default_core=None):
        self.format = format or 'stderr'
        self.logfile = logfile
        self.log_line_prefix = log_line_prefix
        self.output_folder = output_folder
        self.default_core = default_core
        self.parent = parent

    def run(self, dest_path=None,start_ts=None,**kwargs):
        call_list = ['sudo', 'pgbadger',self.logfile]
        filename = '%s.html' %getUuid()
        dest_path = self.parent.getStaticPath(self.output_folder,'pgbadger',filename,autocreate=-1)
        call_list.append('-o')
        call_list.append(dest_path)
        call_list.append('-f')
        call_list.append(self.format)
        if start_ts:
            call_list.append('-b')
            call_list.append(str(start_ts).split('.')[0])
        result = call(call_list)
        if result !=0:
            return None
        return self.parent.getStaticUrl(self.output_folder,'pgbadger',filename)






        #name,ext = os.path.splitext(dest_path)
        #counter = 0
        #while os.path.exists(dest_path):
        #    dest_path = '%s_%i%s'%(name,counter,ext)
        #    counter +=1
        #return_path = dest_path
        #if not os.path.isabs(src_path):
        #    src_path = self.parent.getStaticPath('site:%s'%src_path, autocreate=-1)
        #    dest_path = self.parent.getStaticPath('site:%s'%dest_path, autocreate=-1)
        #call_list = ['abiword', '--to=pdf', src_path, '-o', dest_path]
        #print call_list
        #result = call(call_list)
        #if result !=0:
        #    return None
        #return return_path



"""
pgbadger [options] logfile [...]

            PostgreSQL log analyzer with fully detailed reports and charts.

    Arguments:

        logfile can be a single log file, a list of files, or a shell command
        returning a list of files. If you want to pass log content from stdin
        use - as filename. Note that input from stdin will not work with csvlog.

    Options:
        -j | --jobs number     : number of jobs to run on parallel on each log file.
                                 Default is 1, run as single process.
        -J | --Jobs number     : number of log file to parse in parallel. Default
                                 is 1, run as single process.
        -a | --average minutes : number of minutes to build the average graphs of
                                 queries and connections.
        -b | --begin datetime  : start date/time for the data to be parsed in log.
        -d | --dbname database : only report on entries for the given database.
        -e | --end datetime    : end date/time for the data to be parsed in log.
        -f | --format logtype  : possible values: syslog,stderr,csv. Default: stderr
        -o | --outfile filename: define the filename for output. Default depends on
                                 the output format: out.html, out.txt or out.tsung.
                                 To dump output to stdout use - as filename.



        -l | --last-parsed file: allow incremental log parsing by registering the
                                 last datetime and line parsed. Useful if you want
                                 to watch errors since last run or if you want one
                                 report per day with a log rotated each week.



       

        -p | --prefix string   : give here the value of your custom log_line_prefix
                                 defined in your postgresql.conf. Only use it if you
                                 aren't using one of the standard prefixes specified
                                 in the pgBadger documentation, such as if your prefix
                                 includes additional variables like client ip or
                                 application name. See examples below.

        -q | --quiet           : don't print anything to stdout, even not a progress bar.
        -s | --sample number   : number of query samples to store/display. Default: 3
        -S | --select-only     : use it if you want to report select queries only.
        -t | --top number      : number of queries to store/display. Default: 20
        -T | --title string    : change title of the HTML page report.
        -u | --dbuser username : only report on entries for the given user.
        -U | --exclude-user username : exclude entries for the specified user from report.
    """