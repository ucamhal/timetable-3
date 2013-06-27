from django.utils.datetime_safe import date

TERM_START_DAY = "thu"
TERM_STARTS = {
    2011: (date(2011, 10,  4), date(2012,  1, 17), date(2012,  4, 24)),
    2012: (date(2012, 10,  2), date(2013,  1, 15), date(2013,  4, 23)),
    2013: (date(2013, 10,  8), date(2014,  1, 14), date(2014,  4, 22)),
    2014: (date(2014, 10,  7), date(2015,  1, 13), date(2015,  4, 21)),
    2015: (date(2015, 10,  6), date(2016,  1, 12), date(2016,  4, 19)),
    2016: (date(2016, 10,  4), date(2017,  1, 17), date(2017,  4, 25)),
    2017: (date(2017, 10,  3), date(2018,  1, 16), date(2018,  4, 24)),
    2018: (date(2018, 10,  2), date(2019,  1, 15), date(2019,  4, 23)),
    2019: (date(2019, 10,  8), date(2020,  1, 14), date(2020,  4, 21)),
    2020: (date(2020, 10,  6), date(2021,  1, 19), date(2021,  4, 27)),
    2021: (date(2021, 10,  5), date(2022,  1, 18), date(2022,  4, 26)),
    2022: (date(2022, 10,  4), date(2023,  1, 17), date(2023,  4, 25)),
    2023: (date(2023, 10,  3), date(2024,  1, 16), date(2024,  4, 23)),
    2024: (date(2024, 10,  8), date(2025,  1, 21), date(2025,  4, 29)),
    2025: (date(2025, 10,  7), date(2026,  1, 20), date(2026,  4, 28)),
    2026: (date(2026, 10,  6), date(2027,  1, 19), date(2027,  4, 27)),
    2027: (date(2027, 10,  5), date(2028,  1, 18), date(2028,  4, 25)),
    2028: (date(2028, 10,  3), date(2029,  1, 16), date(2029,  4, 24)),
    2029: (date(2029, 10,  2), date(2030,  1, 15), date(2030,  4, 23))
}

TERM_MICHAELMAS, TERM_LENT, TERM_EASTER = "michaelmas", "lent", "easter"
TERMS = {
    TERM_MICHAELMAS: 0,
    TERM_LENT: 1,
    TERM_EASTER: 2
}
TERMS_REVERSE = dict((v,k) for k,v in TERMS.items())

YEAR_BOUNDARIES = {
    "START": {
        "MONTH": 9,
        "DAY": 1
    },
    "END": {
        "MONTH": 8,
        "DAY": 31
    }
}

class Term(object):
    def __init__(self, name, start):
        self.name = name
        self.start = start

    def to_json(self):
        return {
            "name": self.name,
            "start": self.start.isoformat()
        }

class AcademicYear(object):
    def __init__(self, year, start_boundary, end_boundary, terms):
        self.year = year
        self.start_boundary = start_boundary
        self.end_boundary = end_boundary
        self.terms = terms

    @classmethod
    def for_year(cls, year):
        from timetables.utils.datetimes import termweek_to_date

        if not year in TERM_STARTS:
            raise ValueError("Unknown year: %s. Expected one of: %s" % (
                year, TERM_STARTS.keys()))

        start_boundary = date(
            year, YEAR_BOUNDARIES["START"]["MONTH"],
            YEAR_BOUNDARIES["START"]["DAY"])

        end_boundary = date(
            year + 1,
            YEAR_BOUNDARIES["END"]["MONTH"],
            YEAR_BOUNDARIES["END"]["DAY"])

        terms = []
        for term_name in TERMS:
            start_date = termweek_to_date(year, term_name, 1, TERM_START_DAY)
            terms.append(Term(term_name, start_date))

        return cls(year, start_boundary, end_boundary, terms)

    def get_terms_json(self):
        terms = []
        for term in self.terms:
            terms.append(term.to_json())
        return terms
