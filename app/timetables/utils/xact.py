
""" This code provides a decorator / context manager for transaction management in
    Django on PostgreSQL.  It is intended as a replacement for the existing Django
    commit_on_success() function, and provides some nice features:
    
    * Nested transactions: The top-level transaction will be a BEGIN/COMMIT/ROLLBACK
      block; inner "transactions" are implemented as savepoints.
    * Commits even if is_dirty is False, eliminating the mistake of forgetting to set
      the dirty flag when doing database-modifying raw SQL.
    * Better interaction with pgPool II, if you're using it.
    * A workaround for a subtle but nasty bug in Django's transaction management.

    For full details, check the README.md file.
    
    Originally from https://github.com/Xof/xact/blob/master/xact.py 
    Also see http://thebuild.com/blog/
    
    Modified to support http response codes as well as exceptions.
"""

from functools import wraps

from django.db import transaction, DEFAULT_DB_ALIAS, connections

try:
    import psycopg2.extensions
    PG_INSTALLED = True
except:
    PG_INSTALLED = False

from django.http import HttpResponse

import logging
log = logging.getLogger(__name__)
del logging

class _Transaction(object):
    def __init__(self, using):
        self.using = using
        self.sid = None
        self.complete = False
        self.outer = True

    def __enter__(self):
        if transaction.is_managed(self.using):
            if connections[self.using].features.uses_savepoints:
                # We're already in a transaction; create a savepoint.
                log.debug("-SP-------BEGIN----------------")
                self.sid = transaction.savepoint(self.using)
            self.outer = False
        else:
            log.debug("-O--------BEGIN----------------")
            transaction.enter_transaction_management(using=self.using)
            transaction.managed(True, using=self.using)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.complete:
            return False
        if exc_value is None:
            # commit operation no exception.
            if self.outer and self.sid is None:
                # Outer transaction
                try:
                    log.debug("-O--------COMMIT----------------")
                    transaction.commit(self.using)
                except:
                    log.debug("-O--------ROLLBACK--------------")
                    transaction.rollback(self.using)
                    raise
                finally:
                    self._leave_transaction_management()
            elif self.sid is not None:
                # Inner savepoint
                try:
                    log.debug("-SP-------COMMIT----------------")
                    transaction.savepoint_commit(self.sid, self.using)
                except:
                    log.debug("-SP-------ROLLBACK--------------")
                    transaction.savepoint_rollback(self.sid, self.using)
                    raise
        else:
            # rollback operation there was an exception.
            if self.outer and self.sid is None:
                # Outer transaction
                log.debug("-O--------ROLLBACK--------------")
                transaction.rollback(self.using)
                self._leave_transaction_management()
            elif self.sid is not None:
                # Inner savepoint
                log.debug("-SP-------ROLLBACK--------------")
                transaction.savepoint_rollback(self.sid, self.using)
        return False

    def _leave_transaction_management(self):
        transaction.managed(False, using=self.using)
        transaction.leave_transaction_management(using=self.using)
        if not connections[self.using].is_managed() and connections[self.using].features.uses_autocommit:
            if PG_INSTALLED:
                connections[self.using]._set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                # Patch for bug in Django's psycopg2 backend; see:
                # https://code.djangoproject.com/ticket/16047


class _TransactionWrapper():

    def __init__(self, using):
        self.using = using

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            t = _Transaction(self.using)
            with t:
                o = func(*args, **kwargs)
                if hasattr(o, "status_code"):
                    # If the response is a http response object and the status code indicates
                    # any sort of failure, roll back either the savepoint or the whole
                    # transaction
                    if o.status_code < 200 or o.status_code >= 400:
                        if t.outer and t.sid is None: # outer transaction
                            log.debug("-OR-------ROLLBACK--------------")
                            transaction.rollback(t.using)
                            t._leave_transaction_management()
                        elif t.sid is not None:
                            log.debug("-ORSP-----ROLLBACK--------------")
                            transaction.savepoint_rollback(t.sid, t.using)
                        t.complete = True
                return o
        return inner


def xact(using=None):
    if using is None:
        using = DEFAULT_DB_ALIAS
    if callable(using):
        return _TransactionWrapper(DEFAULT_DB_ALIAS)(using)
    return _TransactionWrapper(using)


# -----------------------------------------------------------------------------
# This software is licensed under the PostgreSQL License:
#
#   http://www.postgresql.org/about/licence/
# 
# Copyright (c) 2012 Christophe Pettus
# 
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written agreement is
# hereby granted, provided that the above copyright notice and this paragraph
# and the following two paragraphs appear in all copies.
# 
# IN NO EVENT SHALL CHRISTOPHE PETTUS BE LIABLE TO ANY PARTY FOR DIRECT,
# INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
# PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN
# IF CHRISTOPHE PETTUS HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
# 
# CHRISTOPHE PETTUS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND POSTGRESQL EXPERTS, INC. HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
