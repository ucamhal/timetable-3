'''
Created on Oct 17, 2012

@author: ieb
'''
import datetime
from django.utils.timezone import utc
import logging


class DateConverter(object):
    '''
    This is a TimeZone and iCal aware date converter
    '''
    
    @staticmethod
    def to_datetime(d):
        '''
        Converts a date into a datetime setting the timezone to utc to enable storage in a datetimefield.
        A seperate flag must be used to indicate that this was a date for the reverse to be possible.
        :param d:
        '''
        if isinstance(d, datetime.datetime):
            return d
        if isinstance(d, datetime.date):
            ## We have to be really carefull here. The date must be converted to 
            ## a date time in GMT for storage.
            return datetime.datetime(d.year,d.month,d.day,tzinfo=utc)
        return d
    
    @staticmethod
    def is_date(d):
        return not isinstance(d, datetime.datetime) and isinstance(d, datetime.date)
    
    @staticmethod
    def from_datetime(d, isallday):
        '''
        Converts a datetime back into a date respecting the isallday flag
        :param d: the datetime
        :param isallday: True if the datetime
        '''
        if isallday:
            return datetime.date(d.year, d.month, d.day)
        return d