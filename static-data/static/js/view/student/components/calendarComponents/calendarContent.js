define(["jquery", "underscore", "util/page", "view/student/components/calendarComponents/listView", "fullcalendar"], function ($, _, page, ListView) {
	"use strict";

	var CalendarContent = function (opt) {
		// Bind event handlers to always have this as a CalendarContext instance
		_.bindAll(this, "onEventClick");

		_.extend(this, opt);
		this.initialize();
	};

	_.extend(CalendarContent.prototype, {
		initialize: function () {
			var sourcepath = page.getThingPath(),
				self = this;

			_.defaults(this, {
				selector: "body",
				activeView: "agendaWeek",
				$el: $(this.selector, this.parent.$el),
				activeTerm: "michaelmas",
				listView: new ListView({
					selector: "#listView",
					parent: this
				}),
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
			if (this.activeView === "list") {
				this.renderListView();
			}
		},

		showPrev: function () {
			this.clearCalendarPopups();
			this.$el.fullCalendar("prev");
			if (this.activeView === "list") {
				this.renderListView();
			}
		},

		renderListView: function () {
			console.log(this.listView);
			this.listView.render({
				year: this.getYearFromDate(this.getActiveDate()),
				month: this.getMonthFromDate(this.getActiveDate())
			});
		},

		clearCalendarPopups: function () {
			$(".calendarEventInfo").each(function () {
				if (!$(this).is(".dontDisplayMe")) {
					$(this).remove();
				}
			});
		},

		setView: function (view) {
			this.clearCalendarPopups();
			this.activeView = view;

			if (view === "list") {
				$(".fc-content", this.$el).hide();
				this.$el.fullCalendar("changeView", "month");
				this.renderListView();
				this.listView.$el.show();
			} else {
				$(".fc-content", this.$el).show();
				this.listView.$el.hide();
				this.$el.fullCalendar("changeView", view);
			}
		},

		getActiveDate: function () {
			return this.$el.fullCalendar("getDate");
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

		dateWithinTerm: function (date, termYears) {

			var dateDay = Number(this.getDayFromDate(date)),
				dateMonth = Number(this.getMonthFromDate(date)),
				dateYear = Number(this.getYearFromDate(date)),
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

				activeDate = $.fullCalendar.parseDate(this.getMonthFromDate(this.getActiveDate()) + " " + this.getDayFromDate(this.getActiveDate()) + " " + this.getYearFromDate(this.getActiveDate())),
				activeYear = this.getYearFromDate(activeDate),

				singleDay = 1000 * 60 * 60 * 24,
				singleWeek = singleDay * 7,

				activeTermData,
				termStartDateObject,
				dayOffset;

			if (this.activeTerm) {
				activeTermData = this.terms[this.activeTerm][activeYear];
				termStartDateObject = $.fullCalendar.parseDate(activeTermData.start.month + " " + activeTermData.start.day + " " + activeYear);

				switch (this.getShortDayFromDate(termStartDateObject)) {
				case "Mon":
					dayOffset = singleDay * 0;
					break;
				case "Tue":
					dayOffset = singleDay * 1;
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
			var $calendarEl = this.$el;

			var $newPopup = $(".calendarEventInfo.dontDisplayMe.student").clone().removeClass("dontDisplayMe");
			var $parent = (function () {
				switch (view.name) {
				case "agendaWeek":
					return $("> div > div", view.element);
					break;
				case "month":
					return self.$el;
					break;
				default:
					return view.element;
				}
			}());

			// The path to the endpoint to GET/POST the event edit form from/to
			var editFormPath = "/events/edit/" + encodeURIComponent(calEvent.djid);

			function insertForm (form) {
				var $form = $(form);

				// kill any existing forms
				$newPopup.find("form").remove();
				// insert the fetched form into the dialog.
				$newPopup.find(".progress").after($form);

				$("*", $newPopup).show();
				$(".progress", $newPopup).hide();
				$form.find(".timepicker-default").timepicker({defaultTime: "value"});
				$form.find(".datepicker").datepicker();
				$parent.trigger("scroll");

				$form.data("submit", function() {
					var formData = $form.serialize();
					return $.post(editFormPath, formData, function(data) {

						// Form submit was OK
						if(_.isObject(data)) {
							// Update the calendar event 
							_.extend(calEvent, data);
							$calendarEl.fullCalendar("updateEvent", calEvent);
						}
						// Form was returned w/ errors, redisplay
						else {
							insertForm(data);
						}
					});
				});
			}
			if (page.adminEnabled()) {
				$newPopup = $(".calendarEventInfo.dontDisplayMe.admin").clone().removeClass("dontDisplayMe");
				$("div.progress div", $newPopup).text("Loading event data...");

				// Fetch pre-populated form for the clicked event
				// FIXME: get event id...
				$.get(editFormPath, insertForm);
			} else {				
				$("span.courseDatePattern", $newPopup).text(this.getFullDayFromDate(calEvent._start) + " " + this.getTwelveHourTimeFromDate(calEvent._start));

				$("span.courseLocation", $newPopup).text((function (location) {
					var locationText = location;
					if (typeof location === "undefined" || location.length <= 0) {
						locationText = "No location specified.";
					}
					return locationText;
				}(calEvent.location)));

				$("span.courseLecturer", $newPopup).text((function (lecturers) {
					var lecturersText = "",
						lecturersLength = lecturers.length,
						i;
					if (lecturersLength > 0) {
						if (lecturersLength === 1) {
							lecturersText = lecturers[0];
						} else {
							for (i = 0; i < lecturersLength; i += 1) {
								lecturersText += lecturers[i];

								if (i !== lecturersLength - 1) {
									lecturersText += ", ";
								}
							}
						}

					} else {
						lecturersText = "No lecturers specified."
					}
					return lecturersText;
				}(calEvent.lecturer)));

				$("h5", $newPopup).text(calEvent.title);
			}

			/*
			$(".calendarEventInfo", view.element).fadeOut("10", function () {
				$(this).remove();
			});

			$parent.prepend($newPopup);

			$newPopup.css({
				top: $(jsEvent.currentTarget).offset().top - $parent.offset().top + $parent.scrollTop() - ($newPopup.outerHeight() / 2) + ($(jsEvent.currentTarget).outerHeight() / 2) - 8,
				left: $(jsEvent.currentTarget).offset().left - $(view.element).offset().left + $(jsEvent.currentTarget).outerWidth() + 10,
				display: "none"
			}).fadeIn("10");
			*/

			$(".calendarEventInfo").each(function () {
				if (!$(this).is(".dontDisplayMe")) {
					$(this).fadeOut("10", function () {
						$(this).remove();
					});
				}
			});

			$("body").append($newPopup);
			$newPopup.css({
				top: $(jsEvent.currentTarget).offset().top - ($newPopup.outerHeight() / 2 - $(jsEvent.currentTarget).outerHeight() / 2),
				left: $(jsEvent.currentTarget).offset().left + $(jsEvent.currentTarget).outerWidth() + 10
			});

			$("a", $newPopup).click(function (event) {
				switch ($(this).text().toLowerCase()) {
				case "save":
					console.log("save");
					var $form = $("form", $newPopup);
					$form.hide();
					var jqxhr = $form.data("submit")();

					$(".progress", $newPopup).show().find("div").text("Saving event...");
					$parent.trigger("scroll");

					jqxhr.always(function(){
						$("*", $newPopup).show();
						$(".progress", $newPopup).hide();
						$parent.trigger("scroll");
					}).fail(function() {
						// called if POST fails
						console.error("oh noes! form submit failed");
						$form.show();
					});
					break;
				case "remove event":
					console.log("remove event");
					break;
				case "cancel":
					$newPopup.remove();
					$parent.unbind("scroll");
				}

				event.preventDefault();
			});

			$parent.scroll(function () {
				if ($(jsEvent.currentTarget).offset().top < $parent.offset().top || $(jsEvent.currentTarget).offset().top + $(jsEvent.currentTarget).outerHeight() > $parent.offset().top + $parent.outerHeight()) {
					$newPopup.fadeOut("10", function () {
						$newPopup.remove();
					});
				} else {
					$newPopup.css({
						top: $(jsEvent.currentTarget).offset().top - ($newPopup.outerHeight() / 2 - $(jsEvent.currentTarget).outerHeight() / 2),
						left: $(jsEvent.currentTarget).offset().left + $(jsEvent.currentTarget).outerWidth() + 10
					});
				}
			});
		}
	});

	return CalendarContent;
});