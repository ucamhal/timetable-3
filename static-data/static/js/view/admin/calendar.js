define([
	"jquery",
	"underscore",
	"backbone",
	"fullcalendar"
], function ($, _, Backbone) {
	"use strict";

	var FullCalendarView = Backbone.View.extend({
		initialize: function (opts) {
			this.$el.fullCalendar({
				defaultView: this.options.defaultView || "month",
				events: this.options.eventsFeed,
				allDaySlot: false,
				minTime: this.options.minTime || 7,
				maxTime: this.options.maxTime || 20,
				header: false,
				firstDay: this.options.firstDay || 1,
				columnFormat: {
					week: "ddd dd/M"
				}
			});

			this.goToDate();
		},

		events: {
			"eventClick": "onEventClick"
		},

		/**
		 * Eventhandler that is triggered when an event on the calendar has been clicked
		 */
		onEventClick: function () {
			console.log("event has been clicked");
		},

		/**
		 * This returns the currently active date in the calendar
		 * @return {object} Returns a date object.
		 */
		getActiveDate: function () {
			return this.$el.fullCalendar("getDate");
		},

		/**
		 * Sets the fullCalendar view to something different e.g. "agendaWeek"
		 * @param {string} view The view that has to be activated.
		 */
		setView: function (view) {
			this.$el.fullCalendar("changeView", view);
		},

		/**
		 * Gets the active view object from fullCalendar (http://arshaw.com/fullcalendar/docs/views/getView/)
		 * @return {object} Returns a fullCalendar View object.
		 */
		getView: function () {
			return this.$el.fullCalendar("getView");
		},

		/**
		 * Moves the calendar to the specified date. Will manipulate the date to always go to the start of the week (Thursday)
		 * @param {object} date The date the calendar has to move to.
		 */
		goToDate: function (date) {
			this.$el.fullCalendar("gotoDate", date);
			return this.getActiveDate();
		}
	});



	var DateSpinner = Backbone.View.extend({

		events: {
			"click .js-prev" : "onPrevious",
			"click .js-next" : "onNext"
		},

		initialize: function (opts) {
			this.type = opts.type || "week";

			if (typeof opts.calendar !== "undefined" || !(calendar instanceof FullCalendarView)) {
				this.calendar = opts.calendar;
			} else {
				console.error("DateSpinners need an instance of FullCalendarView to operate");
			}

			if (typeof opts.terms !== "undefined") {
				this.terms = opts.terms;
			} else {
				console.error("DateSpinners need a terms object to operate");
			}

			this.render();
		},

		/**
		 * Renders the dateSpinner to expose the correct active values
		 */
		render: function () {
			this.updateActiveTermData();
			this.$(".js-value").text(_.capitalize(this.getValue()));
		},

		/**
		 * Updates the activeTermData object with new values based on the active calendar date
		 */
		updateActiveTermData: function () {
			this.activeTermData = this.getTermDataForDate(this.calendar.getActiveDate());
		},

		/**
		 * Returns the value of the datespinner
		 * @return {string} The current value of the dateSpinner (dependant on the type)
		 */
		getValue: function () {
			var value = "";
			switch (this.type) {
			case "week":
				value = this.getActiveWeekString();
				break;
			case "term":
				value = this.getActiveTermString();
				break;
			}
			return value;
		},

		/**
		 * Returns the currently active week withing the currently active term in a nice string format e.g. Week 3
		 * @return {string} A string representing the currently active week within the active term
		 */
		getActiveWeekString: function () {
			var	activeWeekString = "Outside term";
			if (typeof this.activeTermData !== "undefined" && _.has(this.activeTermData, "week")) {
				activeWeekString = "Week " + this.activeTermData.week;
			}
			return activeWeekString;
		},

		/**
		 * Returns the currently active term in a nice string format
		 * @return {string} The currently active term
		 */
		getActiveTermString: function () {
			var	activeTermString = "No active term";
			if (typeof this.activeTermData !== "undefined" && _.has(this.activeTermData, "term")) {
				activeTermString = this.activeTermData.term;
			}
			return activeTermString;
		},

		/**
		 * Eventhandler that gets triggered when the previous button is clicked
		 * moves the calendar to the correct time
		 */
		onPrevious: function (event) {
			switch (this.type) {
			case "week":
				this.goToPreviousWeek();
				break;
			case "term":
				this.goToPreviousTerm();
				break;
			}
			this.render();
			this.trigger("change");
			event.preventDefault();
		},

		/**
		 * Moves the calendar to the previous week
		 */
		goToPreviousWeek: function () {
			this.calendar.goToDate(new Date(this.calendar.getActiveDate().valueOf() - (1000 * 60 * 60 * 24 * 7)));
		},

		/**
		 * Moves the calendar to the previous term
		 */
		goToPreviousTerm: function () {
			if (typeof this.activeTermData !== "undefined") {
				this.calendar.goToDate(this.getRelativeTermDateFromActiveTerm("backwards"));
			} else {
				this.calendar.goToDate(this.getRelativeTermDateFromDate(this.calendar.getActiveDate(), "backwards"));
			}
		},

		/**
		 * Eventhandler that gets triggered when the next button is clicked
		 * moves the calendar to the correct time
		 */
		onNext: function (event) {
			switch (this.type) {
			case "week":
				this.goToNextWeek();
				break;
			case "term":
				this.goToNextTerm();
				break;
			}
			this.render();
			this.trigger("change");
			event.preventDefault();
		},

		/**
		 * Moves the calendar to the next week
		 */
		goToNextWeek: function () {
			this.calendar.goToDate(new Date(this.calendar.getActiveDate().valueOf() + (1000 * 60 * 60 * 24 * 7)));
		},

		/**
		 * Moves the calendar to the next term
		 */
		goToNextTerm: function () {
			if (typeof this.activeTermData !== "undefined") {
				this.calendar.goToDate(this.getRelativeTermDateFromActiveTerm("forwards"));
			} else {
				this.calendar.goToDate(this.getRelativeTermDateFromDate(this.calendar.getActiveDate(), "forwards"));
			}
		},

		/**
		 * Returns term data for the week the date is in.
		 * @param {object} date This is the date that will be used to find the correct term data.
		 * @param {string} rel Look forwards or backwards from date if date is not a Thursday. (if date is not a thursday it moves to the closest Thursday using the direction defined here)
		 * @return {object} Object containing term data of the term the date falls in.
		 */
		getTermDataForDate: function (date, rel) {
			var terms = this.getTermsForDateYear(date),
				direction = rel || "backwards",
				activeTermData,
				activeDate = this.getClosestThursdayFromDate(date, direction),
				activeDateString = activeDate.getFullYear() + "-" + (String(activeDate.getMonth() + 1).length === 1 ? "0" + (activeDate.getMonth() + 1) : activeDate.getMonth() + 1) + "-" + (String(activeDate.getDate()).length === 1 ? "0" + activeDate.getDate() : activeDate.getDate());

			_.each(terms, function (termData, termName) {
				if (typeof activeTermData === "undefined") {
					_.each(termData, function (weekStartDate, weekNr) {
						if (weekStartDate === activeDateString) {
							activeTermData = {
								week: weekNr,
								date: new Date(weekStartDate),
								term: termName
							}
						}
					});
				}
			});

			return activeTermData;
		},

		/*
		 * Finds first possible next or previous date that falls inside a term. Starts searching from the given date.
		 * @param {object} data The date to start searching from.
		 * @param {string} rel The direction to look, forwards by default.
		 * @return {object} The closest date relative to the provided date that falls inside a term.
		 */
		getRelativeTermDateFromDate: function (date, rel) {
			var direction = rel || "forwards",
				termData,
				termDate = date,
				dateIterator = direction === "forwards" ? (1000 * 60 * 60 * 24 * 7) : -(1000 * 60 * 60 * 24 * 7),
				i = 0;

			while (typeof termData === "undefined" && i < 52) {
				termData = this.getTermDataForDate(termDate, direction);
				termDate = new Date(termDate.valueOf() + dateIterator);
				i += 1;
			}

			return new Date(termData.date);
		},

		/*
		 * Gets the date for the next or previous term based on the currently active term. Remembers the currently active week.
		 * @param {string} rel The direction to go, either forwards of backwards, forwards by default.
		 * @return {object} Date object that falls within next or previous term.
		 */
		getRelativeTermDateFromActiveTerm: function (rel) {
			var activeYear = this.getAcademicStartYearFromDate(this.activeTermData.date),
				termDate = this.calendar.getActiveDate(),
				direction = rel || "forwards";

			switch (this.activeTermData.term) {
			case "michaelmas":
				termDate = direction === "forwards" ? this.terms[activeYear]["lent"][this.activeTermData.week] : this.terms[activeYear - 1]["easter"][this.activeTermData.week];
				break;
			case "lent":
				termDate = direction === "forwards" ? this.terms[activeYear]["easter"][this.activeTermData.week] : this.terms[activeYear]["michaelmas"][this.activeTermData.week];
				break;
			case "easter":
				termDate = direction === "forwards" ? this.terms[activeYear + 1]["michaelmas"][this.activeTermData.week] : this.terms[activeYear]["lent"][this.activeTermData.week];
				break;
			}

			return new Date(termDate);
		},

		/**
		 * Returns the closest thursday from a given date
		 * @param {object} date This is the date to search from.
		 * @param {string} rel "next" or "previous", "previous" by default. Determines whether to look forwards or backwards from given date
		 * @return {object} A date object representing the closest Thursday
		 */
		getClosestThursdayFromDate: function (date, rel) {
			var iteration = rel === "backwards" ? -(1000 * 60 * 60 * 24) : (1000 * 60 * 60 * 24);
			while (date.getDay() !== 4) {
				date = new Date(date.valueOf() + iteration);
			}
			return date;
		},

		/*
		 * Returns all possible terms for the year the given date falls in.
		 * @param {object} The date/year to fetch the terms from.
		 * @return {object} All terms for the provided year.
		 */
		getTermsForDateYear: function (date) {
			var terms = false,
				activeYear = this.getAcademicStartYearFromDate(date);
			if (_.has(this.terms, activeYear)) {
				terms = this.terms[activeYear];
			}
			return terms;
		},

		/**
		 * Gets the academic year from a date object.
		 * @param {object} date The date to get the academic year from.
		 * @return {number} The academic year for the provided date.
		 */
		getAcademicStartYearFromDate: function (date) {
			return date.getMonth() < 9 ? date.getFullYear() - 1 : date.getFullYear()
		}
	});

	return {
		FullCalendarView: FullCalendarView,
		DateSpinner: DateSpinner
	};

});