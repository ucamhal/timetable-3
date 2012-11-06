define([
	"jquery",
	"underscore",
	"util/page",
	"fullcalendar"
], function ($, _, page) {
	"use strict";

	var BaseCalendarContent = function () {

	};

	_.extend(BaseCalendarContent.prototype, {
		baseInitialize: function () {

			var sourcepath = page.getThingPath(),
				self = this;

			// Bind event handlers to always have this as a CalendarContext instance
			_.bindAll(this, "onEventClick");

			_.defaults(this, {
				selector: "body",
				activeView: "agendaWeek",
				$el: $(this.selector, this.parent.$el),
				activeTerm: "michaelmas",
				activePopups: [],
				// #TODO This data should be pulled in from a json file
				terms: {
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
				}
			});

			this.$el.fullCalendar({
				defaultView: this.activeView,
				events: "/" + sourcepath + ".cal.json",
				allDaySlot: false,
				minTime: 7,
				maxTime: 20,
				header: false,
				firstDay: 1,
				columnFormat: {
					week: "ddd dd/M"
				},
				eventClick: this.onEventClick
			});

		},
		refresh: function () {
			this.$el.fullCalendar("refetchEvents");
		},

		showNext: function () {
			this.clearCalendarPopups();
			this.$el.fullCalendar("next");
		},

		showPrev: function () {
			this.clearCalendarPopups();
			this.$el.fullCalendar("prev");
		},

		clearCalendarPopups: function () {
			var i,
				selectedPopup,
				arrayLength = this.activePopups.length;

			for (i = 0; i < arrayLength; i += 1) {
				selectedPopup = this.activePopups[i];
				if (selectedPopup instanceof this.CalendarPopup === true) {
					selectedPopup.removeAnimated();
				}
			}
		},

		setView: function (view) {
			this.clearCalendarPopups();
			this.activeView = view;

			$(".fc-content", this.$el).show();
			this.$el.fullCalendar("changeView", view);
		},

		getActiveDate: function () {
			return this.$el.fullCalendar("getDate");
		},

		dateWithinTerm: function (date, termYears) {

			var dateDay = Number(_.getDayFromDate(date)),
				dateMonth = Number(_.getMonthFromDate(date)),
				dateYear = Number(_.getYearFromDate(date)),
				withinPeriod = false,
				term = termYears[dateYear];

			if (term && dateMonth >= term.start.month && dateMonth <= term.end.month) {
				if (!((dateMonth === term.start.month && dateDay < term.start.day) || (dateMonth === term.end.month && dateDay > term.end.day))) {
					withinPeriod = true;
				}
			}

			return withinPeriod;
		},

		getActiveWeekInCurrentTerm: function () {
			var activeWeek,

				activeDate = $.fullCalendar.parseDate(_.getMonthFromDate(this.getActiveDate()) + " " + _.getDayFromDate(this.getActiveDate()) + " " + _.getYearFromDate(this.getActiveDate())),
				activeYear = _.getYearFromDate(activeDate),

				singleDay = 1000 * 60 * 60 * 24,
				singleWeek = singleDay * 7,

				activeTermData,
				termStartDateObject,
				dayOffset;

			if (this.activeTerm) {
				activeTermData = this.terms[this.activeTerm][activeYear];
				termStartDateObject = $.fullCalendar.parseDate(activeTermData.start.month + " " + activeTermData.start.day + " " + activeYear);

				switch (_.getShortDayFromDate(termStartDateObject)) {
				case "Mon":
					dayOffset = 0;
					break;
				case "Tue":
					dayOffset = singleDay;
					break;
				case "Wed":
					dayOffset = singleDay * 2;
					break;
				case "Thu":
					dayOffset = singleDay * 3;
					break;
				case "Fri":
					dayOffset = singleDay * 4;
					break;
				case "Sat":
					dayOffset = singleDay * 5;
					break;
				case "Sun":
					dayOffset = singleDay * 6;
					break;
				}

				activeWeek = Math.round((((activeDate - termStartDateObject) + dayOffset) / singleWeek) + 1);
			}

			return activeWeek;

		},

		getActiveTerm: function () {
			var view = this.$el.fullCalendar("getView"),
				index,
				activeTerm,
				selectedTerm;

			for (index in this.terms) {
				if (this.terms.hasOwnProperty(index) && !activeTerm) {
					selectedTerm = this.terms[index];

					if (this.dateWithinTerm(view.start, selectedTerm) || this.dateWithinTerm(view.end, selectedTerm)) {
						activeTerm = index;
					}
				}
			}

			this.activeTerm = activeTerm;
			return activeTerm;
		},

		setFullCalendarAspectRatio: function (ratio) {
			this.$el.fullCalendar('option', 'aspectRatio', ratio);
		},

		setHeight: function (height) {
			// #TODO FullCalendar doesn't take the max height in agendaWeek view
			// Can be fixed by lowering the slotMinutes option, FullCalendar doesn't however allow us to change this at runtime
			this.$el.fullCalendar('option', 'height', height);
			this.$el.height(height);
		},

		onEventClick: function (calEvent, jsEvent, view) {

			var self = this,
				calendarPopup = new this.CalendarPopup({
					parent: self,
					editFormPath: "/event/" + encodeURIComponent(calEvent.djid),
					calEvent: calEvent,
					jsEvent: jsEvent,
					$scrollReference: (function () {
						var toReturn;
						switch (view.name) {
						case "agendaWeek":
							toReturn = $("> div > div", view.element);
							break;
						case "month":
							toReturn = self.$el;
							break;
						default:
							toReturn = view.element;
						}
						return toReturn;
					}())
				});

			this.clearCalendarPopups();

			$("body").append(calendarPopup.$el);
			calendarPopup.reposition();
			this.activePopups.push(calendarPopup);
		}
	});

	return BaseCalendarContent;

});