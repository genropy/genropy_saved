#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrsql : Genro sql db connection.
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

__version__ = '1.0b'

from gnr.core.gnrlang import GnrException

class GnrSqlException(GnrException): #CHECK THERE IS ANOTHER CLASS WITH THE SAME NAME INSIDE GNRSQL 
    """Exceptions raised for sql errors
        
    :param code: error code
    :param message: explanation of the error
    """
    def __init__(self, code, message=None):
        if not message and ':' in code:
            code, message = code.split(':', 1)
        self.code = code
        self.message = message
        
class GnrNonExistingDbException(GnrSqlException):
    def __init__(self, dbname):
        self.dbname = dbname
        
class NotMatchingModelError(GnrSqlException):
    pass
        
class GnrSqlApplicationException(GnrSqlException):
    pass
        
class GnrSqlExecutionException(GnrSqlException):
    """Exceptions raised for sql execution errors
    
    :param code: error code
    :param message: explanation of the error
    :param sql: TODO
    :param params: TODO
    """
    
    def __init__(self, code, message, sql, params):
        self.code = code
        self.message = message
        self.sql = sql
        self.params = params
        
class GnrSqlSaveException(GnrSqlException):
    """Exceptions raised for sql errors"""
    pass
        
class GnrSqlDeleteException(GnrSqlException):
    """Exceptions raised for sql errors"""
    pass
        
class NotMatchingModelError(GnrSqlException):
    pass
        
class SelectionExecutionError(GnrException):
    pass
        
class RecordDuplicateError(GnrException):
    pass
        
class RecordNotExistingError(GnrException):
    pass
        
class RecordSelectionError(GnrException):
    pass
        
class GnrSqlMissingField(GnrException):
    pass
        
class GnrSqlMissingTable(GnrException):
    pass
        
class GnrSqlMissingColumn(GnrException):
    pass
        
class GnrSqlRelationError(GnrException):
    pass
        