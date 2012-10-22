#!/usr/bin/env python
import logging
import sys, os
import subprocess
import traceback
error = 0
logging.error("Checking Dependencies ")
THIS_LOCATION =  os.path.dirname(os.path.abspath(__file__))
workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("%s/app" % workspace)
os.environ['DJANGO_SETTINGS_MODULE'] = 'timetables.settings'


try:
    from django.db import models 
    logging.error("DJango Found Ok ")
except:
    logging.error(traceback.format_exc())
    logging.error("Oh Dear, no DJango present you need to install with easy_install django or some other method, see the README")
    error = 1
    
try:
    from south.db import db
    logging.error("South Found Ok ")
except:
    logging.error(traceback.format_exc())
    logging.error("Please install South for data migration with easy_install South or some other method, see the README")
    error = 1

# add python dependencies above here with try, except


# add OS level commands as ( [args], retcode )

CHECK_COMMANDS = (
        (['python','--version'],0),
        )
for c,ret in CHECK_COMMANDS:
    try:
        i = subprocess.call(c,stdout=None,stderr=None)
        if i == ret or i == 0:
            logging.error("Command %s Ok" % c)
        else:
            logging.error("Command %s Returned Non zero code %s " % (c,i))
            error = 1
    except:
        logging.error("Command %s failed " % c)
        error = 1

if error != 0:
    logging.error("Some missing dependencies, please correct and retry deploy build")
else:
    logging.error("Dependencies checked Ok.")
        
sys.exit(error)

