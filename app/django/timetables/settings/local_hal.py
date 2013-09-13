from timetables.settings.local import *


INSTALLED_APPS += (
#    "devserver",
#    "django_extensions",
)

DEBUG = True
TEMPLATE_DEBUG = True

#DEVSERVER_AJAX_PRETTY_PRINT = True

# Set True to profile every request
#DEVSERVER_AUTO_PROFILE = False

# Configure the data printed for each request. The order here is not
# necessarily the order output appears in as modules can produce their
# output at differnt stages of the request/resposne lifecycle.
DEVSERVER_MODULES = (
    "devserver.modules.request.RequestDumpModule",
    'devserver.modules.sql.SQLRealTimeModule',
    'devserver.modules.sql.SQLSummaryModule',
    'devserver.modules.profile.ProfileSummaryModule',
    'devserver.modules.profile.MemoryUseModule',
    'devserver.modules.cache.CacheSummaryModule',
    'devserver.modules.profile.LineProfilerModule',
    'devserver.modules.request.SessionInfoModule',
    "devserver.modules.request.ResponseDumpModule",
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'timetable',
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}