'''
Created on Jul 23, 2012

@author: ieb
'''

import hotshot
import os
import time
from django.conf import settings

import logging
log = logging.getLogger(__name__)
sqllog = logging.getLogger("SQL")
del logging

from django.db import connection
import traceback


try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"

try:
    DUMP_FULL_SQL = settings.DUMP_FULL_SQL
except:
    DUMP_FULL_SQL = False


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.     
    
    
    To use add the annotation
          @profile("createuser")
          
          to a method which will create /tmp/createuser-20120620T063316
          then list the profile with 
          
          python print-profile.py /tmp/createuser-20120620T063316

    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer


class SQLProfileMiddleware(object):

    def process_response(self, request, response):
        t = 0.0
        for q in connection.queries: #@UndefinedVariable
            t = t + float(q['time'])
        if "GET" == request.method:
            nmax = 20
            tmax = 0.05
        else:
            nmax = 100
            tmax = 0.1
        #
        # The log statements here are set to error level because its an error
        # to exceed the sql query thresholds. Please do not set them to info or
        # debug as this will hide the errors from the developer when they are created.
        # to disable output set DUMP_FULL_SQL to False in local_settings.py
        #
        if hasattr(request, "_dump_sql") and not request._dump_sql:
            sqllog.error("SQL PROFILE DISABLED FOR THIS REQUEST: don't set request._dump_sql = False")
            return response
        if '_dump_sql' in request.REQUEST or \
                hasattr(request, "_dump_sql") or \
                (len(connection.queries) > nmax or \
                t > tmax): #@UndefinedVariable
            if DUMP_FULL_SQL:
                sqllog.error("------------------------- Start SQL Timing Dump --------------------------------");
                for q in sorted(connection.queries, key=lambda k: float(k['time'])): #@UndefinedVariable
                    sqllog.error(q)
                sqllog.error("------------------------- End SQL Timing Dump   --------------------------------");
            sqllog.error(" %s statements took %s seconds " % (len(connection.queries), t)) #@UndefinedVariable
        return response

    def process_exception(self, request, exception):
        log.debug("Exception %s " % traceback.format_exc())
        return None
