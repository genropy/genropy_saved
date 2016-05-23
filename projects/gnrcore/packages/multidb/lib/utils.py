# encoding: utf-8

from gnr.sql.gnrsql import GnrSqlException

class GnrMultidbException(GnrSqlException):
    """Standard Genro SQL Business Logic Exception
    
    * **code**: GNRSQL-101
    """
    code = 'GNRSQL-101'
    description = '!!%(description)s'
    caption = '!!%(msg)s'