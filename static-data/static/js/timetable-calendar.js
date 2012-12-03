define(["jquery", "underscore", "view/admin/calendar", "bootstrap", "fullcalendar"], function($, _, Calendar) {
    "use strict";

    _.mixin({
		capitalize: function (string) {
			return string.charAt(0).toUpperCase() + string.substring(1).toLowerCase();
		},

		addEventListener: function (to, eventName, callback) {
			to.bind(eventName, callback);
		},

		dispatchEvent: function (from, eventName, extraParameters) {
			from.trigger(eventName, extraParameters);
		},

		getDayFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "d");
		},

		getShortDayFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "ddd");
		},

		getFullDayFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "dddd");
		},

		getMonthFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "M");
		},

		getYearFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "yyyy");
		},

		getFullMonthFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "MMMM");
		},

		getTwelveHourTimeFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "h(':'mm)tt");
		},

		getTwentyFourHourFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "H");
		},

		getMinutesFromDate: function (date) {
			return $.fullCalendar.formatDate(date, "mm");
		}
	});

    var calendar = new Calendar.FullCalendarView({
    	el: $(".js-calendar"),
    	defaultView: "agendaWeek",
    	firstDay: 4
    });

    var terms = {
		michaelmas: {
			2012: {
				start: {
					day: 4,
					month: 10
				},
				end: {
					day: 2,
					month: 12
				}
			},
			2013: {
				start: {
					day: 2,
					month: 10
				},
				end: {
					day: 30,
					month: 11
				}
			},
			2014: {
				start: {
					day: 8,
					month: 10
				},
				end: {
					day: 6,
					month: 12
				}
			},
			2015: {
				start: {
					day: 7,
					month: 10
				},
				end: {
					day: 5,
					month: 12
				}
			},
			2016: {
				start: {
					day: 6,
					month: 10
				},
				end: {
					day: 4,
					month: 12
				}
			}
		},

		lent: {
			2013: {
				start: {
					day: 15,
					month: 1
				},
				end: {
					day: 15,
					month: 3
				}
			},
			2014: {
				start: {
					day: 14,
					month: 1
				},
				end: {
					day: 14,
					month: 3
				}
			},
			2015: {
				start: {
					day: 13,
					month: 1
				},
				end: {
					day: 13,
					month: 3
				}
			},
			2016: {
				start: {
					day: 12,
					month: 1
				},
				end: {
					day: 11,
					month: 3
				}
			}
		},

		easter: {
			2013: {
				start: {
					day: 23,
					month: 4
				},
				end: {
					day: 14,
					month: 6
				}
			},
			2014: {
				start: {
					day: 22,
					month: 4
				},
				end: {
					day: 13,
					month: 6
				}
			},
			2015: {
				start: {
					day: 21,
					month: 4
				},
				end: {
					day: 12,
					month: 6
				}
			},
			2016: {
				start: {
					day: 19,
					month: 4
				},
				end: {
					day: 10,
					month: 6
				}
			}
		}
	};

	var weekSpinner = new Calendar.DateSpinner({
		el: ".js-date-spinner.js-week",
		type: "week",
		calendar: calendar,
		terms: terms
	});

	var termSpinner = new Calendar.DateSpinner({
		el: ".js-date-spinner.js-term",
		type: "term",
		calendar: calendar,
		terms: terms
	});

	weekSpinner.on("change", function () {
		termSpinner.render();
	});

	termSpinner.on("change", function () {
		weekSpinner.render();
	});

    return undefined;
});