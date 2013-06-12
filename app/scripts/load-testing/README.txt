=======================
Timetables Load Testing
=======================

This directory contains files related to load testing Timetables. Apache
JMeter( http://jmeter.apache.org/ ) is the primary tool we use to perform load
testing.

JMeter uses "test plans" to specify what a load test run should do. A typical
(http) load test consists of a selection of URLs to hit in a sequence, a number
of users (threads) to run through these URLs at once, and a way of monitoring
the results of hitting the URLs.

If you're new to JMeter and or load testing then you should at minimum read:
http://jmeter.apache.org/usermanual/boss.html and preferably the relavent parts
of the manual: http://jmeter.apache.org/usermanual/index.html and keep the
component reference handy:
http://jmeter.apache.org/usermanual/component_reference.html -- use this if you
see a node in a test plan's tree and you don't know what it does.

The following blog post may also be of interest:
http://lincolnloop.com/blog/2011/sep/21/load-testing-jmeter-part-1-getting-started/

Also the "User Experience, not Metrics Series" section of:
http://www.perftestplus.com/pubs.htm (plus other interesting things on that
page).


JMeter configuration
====================

JMeter should be configured to store received cookies as JMeter thread variables.
See http://jmeter.apache.org/usermanual/component_reference.html#HTTP_Cookie_Manager
for details.

Edit jmeter.properties file to set configuration.

Theoretically properties may be configured in the JMeter test plan using the
Simple Config Element, but this doesn't currently seem to be working.


Test Plans
==========

Currently there is a single JMeter test plan at timetables-load-test.jmx.

This plan implements a load test rather than a stress test in the sense that it
aims to mimic the load of a specific number of concurrent users rather than
attemping measure the maximum throughput of the site.

The plan tries to mimic a user by taking the following actions each iteration of
each user's (thread's) run:

 * Log in by GETing the login page, POSTing to the login page & then fetching
   the user's calendar (as this would be fetched when the homepage loads after
   the login POST redirects to the homepage)
 * Loop a number of times, each time GETing a random URL from a list of available
   URLs. The rate of iteration is limited by a random timer.

Note that the root of the test plan tree holds several variables used further
down the tree.

Because we don't yet know how real users will use the site, this test plan
represents an educated guess with a significant fudge factor. I err on the site
of overestimating the load of an 'average' user rather than underestimating.

We don't yet have any requirements to try to meet for:
 * typical number of concurrent users
 * peak number of concurrent users
 * response times

As such, when these are known the plan will need to be updated to reflect these.
For example, adjusting the plan's number of users (threads).
