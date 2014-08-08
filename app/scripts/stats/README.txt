Timetable Stat Generation
~~~~~~~~~~~~~~~~~~~~~~~~~

Fetch Access Logs
-----------------

Run the following to fetch access logs for www.timetable.cam.ac.uk (vast05)
    $ python logfetch.py -u hwtb2 --insecure \
        'https://syslog.dmz.caret.local/vast05.ds.lib.cam.ac.uk/httpd-access/' \
        2013-09-22 \
        > /Volumes/Timetable\ Data/http-access--2013-09-22--2013-10-15.log

After fetching the logs, the syslog cruft needs to be stripped from each line, and the logs parsed into a JSON document listing iCal fetches by CRSID. This can be done in one step as follows:

	$ python logfetch.py -u hwtb2 --insecure 'https://syslog.dmz.caret.local/vast05.ds.lib.cam.ac.uk/httpd-access/' 2014-01-02 2014-05-01 | python stripsyslogbs.py | python log2json.py - > /Volumes/Timetable\ Data/2014-08-06/access_logs/ical-access-2014-01-02--2014-05-01.json

You can use jsonmerge.py to merge individual JSON access log files.


Fetch raw user data from the webapp db
--------------------------------------

We need the contents of a user's calendar from the Timetable DB itself. There's a manage.py command which will export every user's calendar from the db in JSON format. Run 
	$ python manage.py exportusers > /some/file.json


Cleanup
=======

Note that there seem to be some old series without module parents in the db. The exporter will detect these and fail with an error. They should be removed from the db before exporting (in an interactive Python session):

    >>> EventSource.objects.exclude(eventsourcetag__thing__type="module").delete()


Fetch private uni data
----------------------

unicsv2json.py in the app/scripts/stats dir in the timetable repo will create the user JSON needed to identify a user's tripos/year etc. The program's help explains the inputs (-h/--help).

The hard to obtain data was obtained from education section as a spreadsheet.

Merge
-----

Once these 3 data sets have been obtained/generated, they need to be merged into a single JSON file using jsonmerge.py.

Once that's done you run userstats on the resulting merged JSON, then finaly stats2html.py on the generated stats tree to make a human browsable representation.

	$ python -m userstats data-merged.json > data-analysed.json
	$ python stats2html.py data-analysed.json stats2html-templates/ stats-html-SOME_TIMESTAMP

* Note that the output dir needs to exist before running the command.
* Note that userstats takes a lot of memory and time to run.

2014-08-06 run
==============

My most recent run looked as follows. (/Volumes/Timetable Data/ is an encrypted disk image to store the PII.)

	(timetable-stats)11:55:22 hwtb2@Gravel:/Volumes/Timetable Data/2014-08-06
	$ ls -l . access_logs/
	.:
	total 1.2G
	drwxr-xr-x    6 hwtb2 staff  204 Aug  6 14:59 access_logs
	-r--r--r--    1 hwtb2 staff  34M Aug  6 17:52 data-analysed.json
	-r--r--r--    1 hwtb2 staff 1.1G Aug  6 15:32 data-merged.json
	lrwxr-xr-x    1 hwtb2 staff   51 Aug  6 15:28 ical-access-2013-09-22--2014-08-05.json -> access_logs/ical-access-2013-09-22--2014-08-05.json
	drwxr-xr-x 8350 hwtb2 staff 278K Aug  7 09:34 stats-html-2014-08-06
	-rw-r--r--    1 hwtb2 staff 1.5M Aug  7 09:56 stats-html-2014-08-06.tar.gz
	-rw-r--r--    1 hwtb2 staff 8.3M Aug  7 09:57 stats-html-2014-08-06.zip
	-rwxr-xr-x    1 hwtb2 staff  35M Aug  6 14:34 timetable-users-2014-08-06.json
	-rw-r--r--    1 hwtb2 staff 4.1M Aug  6 15:27 unidata.json

	access_logs/:
	total 2.8G
	-rw-r--r-- 1 hwtb2 staff 450M Aug  6 13:44 ical-access-2013-09-22--2014-01-01.json
	-rw-r--r-- 1 hwtb2 staff 1.1G Aug  6 15:01 ical-access-2013-09-22--2014-08-05.json
	-rw-r--r-- 1 hwtb2 staff 746M Aug  6 14:44 ical-access-2014-01-02--2014-05-01.json
	-rw-r--r-- 1 hwtb2 staff 590M Aug  6 14:50 ical-access-2014-05-02--2014-08-05.json

The vast majority of the data comes from the iCal feed access logs. My computer has 16GB of RAM. Running userstats on data-merged.json took 11-12GB RAM and took ~135 minutes to run.
