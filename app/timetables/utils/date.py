'''
Created on Oct 17, 2012

@author: ieb
'''
import datetime
from django.utils.timezone import utc
import logging
from timetables.utils.datetimes import server_timezone


class DateConverter(object):
    '''
    This is a TimeZone and iCal aware date converter
    '''
    
    @staticmethod
    def to_datetime(d, defaultzone=server_timezone()):
        '''
        Converts a date into a datetime setting the timezone to utc to enable storage in a datetimefield.
        A seperate flag must be used to indicate that this was a date for the reverse to be possible.
        :param d:
        '''
        if isinstance(d, datetime.datetime):
            if d.tzinfo is None:
                # No timezone was specified, so to keep Django happy we have to give it the server timezone.
                # This may not be right from the users point of view, but for a shared application where the 
                # same event may be viewed in multiple timezones its the only way. Its v rare now to 
                # Find a calendar that says "at 10am, in whatever timezone you happen to be in" although
                # that does exists (get out of bed, go to sleep)
                if defaultzone is not None:
                    d = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, tzinfo=defaultzone)
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