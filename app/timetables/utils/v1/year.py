# This code comes from the Timetables V1 Project written by Dan Shepard

import datetime
import copy
import re
from timetables.utils.v1.grouptemplate import GroupTemplate
from timetables.utils.v1 import util
import pytz

term_names = ['Michaelmas','Lent','Easter']

multispace_re = re.compile(r" +")

# XXX within term
class Year:
    def __init__(self,starts):
        '''
        :param starts: an array of dates containing the start of each term in order michalmass, lent, easter
        eg         Year([datetime.date(2012,10,2),datetime.date(2013,1,15),datetime.date(2013,4,23)])

        '''
        self.starts = starts

    def _date(self,term,week,day):
        # day 0 = mon, .... 6 = sun
        days_after_thursday = (day+4) % 7
        # 2 is because we store Tuesday term starts
        return self.starts[term] + datetime.timedelta(days=(week-1)*7) + datetime.timedelta(days = days_after_thursday+2)

    def atoms_to_secular(self,atoms,show_time = True):
        full = []
        short = []
        common = True
        terms = set()
        for atom in atoms:
            for term in atom.getTerms():
                terms.add(term)
        for term in terms:
            for atom in atoms:
                when = []
                weeks = atom.getTermWeeks().weeks_of_term(term)
                for week in weeks:
                    for dt in atom.getDayTimesRaw():
                        (day,time) = dt.rep2()
                        date = self._date(term,week,day)
                        when.append((date,time))
                for (date,time) in sorted(when,key = lambda x: x[0]):
                    daystr = date.strftime("%e %b")
                    full.append("%s at %s" % (daystr,time))
                    short.append(daystr)
                    if common is True:
                        common = time
                    elif common is not False and common != time:
                            common = False
        if show_time:
            if common is not False and common is not True:
                # oclock, etc
                out = "at %s on %s" % (common,", ".join(short))
            else:
                out = ", ".join(full)
        else:
            out = ", ".join(short)
        out = multispace_re.sub(' ',out)
        return out


    def atoms_to_dt(self, atoms, timezone):
        '''
        Convert atoms to date time.
        :param atoms: the atoms
        :param as_datetime: set to False if iso dates
        :param timezone:
        '''
        out = []
        tzinfo = pytz.timezone(timezone)
        for atom in atoms:
            for frag in atom.blast():
                for (term,week) in frag.getTermWeeks().each():
                    for dt in frag.getDayTimesRaw():
                        # This makes the assumption everything happens on the same day.
                        date = self._date(term,week,dt.day)
                        start = tzinfo.localize(datetime.datetime(year=date.year, month=date.month, day=date.day,
                                                  hour=dt.start[0], minute=dt.start[1], second=0,
                                                  microsecond=0))
                        end = tzinfo.localize(datetime.datetime(year=date.year, month=date.month, day=date.day,
                                            hour=dt.end[0], minute=dt.end[1], second=0,
                                            microsecond=0))
                        out.append((start,end,))
        return out

    def to_templated_secular_display(self,fp,group,type= 'lecture'):
        gt = GroupTemplate(None)
        gt.add_patterns(fp)
        gt.calculate_reduction(True)
        out = []
        for (_,_,(pattern,mult)) in gt.get_patterns_raw(False):
            if pattern is None:
                # just multiplier, should be just "x lectures"
                row = "%d %s, %s" % (mult,util.plural(type),gt.template) # XXX proper plurals
            elif mult is None:
                # traditional pattern, expand codes sensibly
                row = "%s %s" % (util.plural(type),self.atoms_to_secular(fp.patterns(),True))
            else:
                # start date and multiplier
                pp = copy.deepcopy(gt.template)
                pp.setAllYear()
                row = "%s %s, starting on %s, %s" % (mult,util.plural(type),self.atoms_to_secular([pattern],False),pp)
            out.append(row)
        prefix = ''
        if group is not None:
            prefix = "%s term, " % term_names[group.term]
        return prefix+", ".join(out)
