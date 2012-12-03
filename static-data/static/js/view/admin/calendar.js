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
			if (date) {
				this.$el.fullCalendar("gotoDate", date);
			}

			//set the calendar active date to the start of the week (Thursday)
			while (this.getActiveDate().getDay() !== 4) {
				this.$el.fullCalendar("gotoDate", new Date(this.getActiveDate().valueOf() - (1000 * 60 * 60 * 24)));
			}

			return this.getActiveDate();
		}
	});

	var DateSpinner = Backbone.View.extend({
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
		 * Returns the value of the datespinner
		 * @return {string} The current value of the dateSpinner (dependant on the type)
		 */
		getValue: function () {
			var value = "";
			switch (this.type) {
			case "week":
				value = this.getActiveWeekInCurrentTermString();
				break;
			case "term":
				value = this.getActiveTermString();
				break;
			}
			return value;
		},

		/**
		 * Returns an object with start and end dates for the given term
		 * @param {string} termName The name of the term
		 * @param {number} year The year you want the dates from
		 * @retun {object} Returns an object with start and end date objects.
		 */
		getDatesFromTermInYear: function (termName, year) {
			return {
				start: new Date(year, this.terms[termName][year].start.month, this.terms[termName][year].start.day),
				end: new Date(year, this.terms[termName][year].end.month, this.terms[termName][year].end.day)
			};
		},

		/*
		 * Checks wether the given date falls within the given term
		 * @param {object} date The date to check.
		 * @param {object} termObject An object containing years and start and end dates per year for the term.
		 * @return {boolean} Returns true when the date falls withing the given term, false if not.
		 */
		dateWithinTerm: function (date, termObject) {

			var dateDay = Number(_.getDayFromDate(date)),
				dateMonth = Number(_.getMonthFromDate(date)),
				dateYear = Number(_.getYearFromDate(date)),
				withinPeriod = false,
				term = termObject[dateYear];

			if (term && dateMonth >= term.start.month && dateMonth <= term.end.month) {
				if (!((dateMonth === term.start.month && dateDay < term.start.day) || (dateMonth === term.end.month && dateDay > term.end.day))) {
					withinPeriod = true;
				}
			}

			return withinPeriod;
		},

		/**
		 * Returns the currently active week withing the currently active term in a nice string format e.g. Week 3
		 * @return {string} A string representing the currently active week within the active term
		 */
		getActiveWeekInCurrentTermString: function () {
			var week = this.getActiveWeekInCurrentTerm();
			return week ? "Week " + week : "Outside term";
		},

		/**
		 * Returns the active week number within the currently active term
		 * @return {number} The active week number withing the term
		 */
		getActiveWeekInCurrentTerm: function () {
			var activeWeek,

				activeDateObject = new Date(this.calendar.getActiveDate().getFullYear(), this.calendar.getActiveDate().getMonth(), this.calendar.getActiveDate().getDate()),

				singleDay = 1000 * 60 * 60 * 24,
				singleWeek = singleDay * 7,

				activeTerm = this.getActiveTerm(),

				activeTermData,
				termStartDateObject,
				dayOffset;

			if (activeTerm) {
				activeTermData = this.terms[activeTerm][activeDateObject.getFullYear()];
				termStartDateObject = new Date(activeDateObject.getFullYear(), activeTermData.start.month - 1, activeTermData.start.day);

				switch (_.getShortDayFromDate(termStartDateObject)) {
				case "Mon":
					dayOffset = singleDay * 4;
					break;
				case "Tue":
					dayOffset = singleDay * 5;
					break;
				case "Wed":
					dayOffset = singleDay * 6;
					break;
				case "Thu":
					dayOffset = 0;
					break;
				case "Fri":
					dayOffset = singleDay;
					break;
				case "Sat":
					dayOffset = singleDay * 2;
					break;
				case "Sun":
					dayOffset = singleDay * 3;
					break;
				}

				activeWeek = Math.round(((activeDateObject.valueOf() - (termStartDateObject.valueOf() - dayOffset)) / singleWeek)) + 1;
			}

			return activeWeek;
		},

		/**
		 * Returns the currently active term in a nice string format
		 * @return {string} The currently active term
		 */
		getActiveTermString: function () {
			var term = this.getActiveTerm();
			return term || "No active term";
		},

		/**
		 * Returns the currently active term
		 * @return {string} the currently active term, e.g. "michaelmas", undefined if active day in calendar falls outside terms.
		 */
		getActiveTerm: function () {
			var view = this.calendar.getView(),
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

			return activeTerm;
		},

		/**
		 * Calculates and returns the active term for a given date
		 * @return {string} the currently active term, e.g. "michaelmas", undefined if the given date falls outside terms.
		 */
		getActiveTermForDate: function (date) {
			var index,
				activeTerm,
				selectedTerm;

			for (index in this.terms) {
				if (this.terms.hasOwnProperty(index) && !activeTerm) {
					selectedTerm = this.terms[index];

					if (this.dateWithinTerm(date, selectedTerm)) {
						activeTerm = index;
					}
				}
			}

			return activeTerm;
		},

		events: {
			"click .js-prev" : "onPrevious",
			"click .js-next" : "onNext"
		},

		/**
		 * Returns either the next or the previous term in line based on the active date in the calendar.
		 * @param {string} rel Either "previous" or "next", determines wether to look forwards or backwards in time
		 * @return {object} An object that contains all necessary term data: the term name, year, start and end dates.
		 */
		getRelativeTerm: function (rel) {
			var calculateTerm = rel === "previous" ? this.getPreviousTerm : this.getNextTerm;
			return calculateTerm.call(this, rel);
		},

		/**
		 * Returns the previous term based on the currently active date in the calendar
		 * @return {object} An object that contains all necessary term data: the term name, year, start and end dates.
		 */
		getPreviousTerm: function () {
			var currentTerm = this.getActiveTerm(),
				previousTerm = {
					year: Number(_.getYearFromDate(this.calendar.getActiveDate()))
				};

			switch (currentTerm) {
			case "michaelmas":
				previousTerm.term = "easter";
				break;
			case "lent":
				previousTerm.term = "michaelmas";
				previousTerm.year -= 1;
				break;
			case "easter":
				previousTerm.term = "lent";
				break;
			default:
				previousTerm = this.getClosestRelativeTermFromDate(this.calendar.getActiveDate(), "previous");
			}

			_.extend(previousTerm, this.terms[previousTerm.term][previousTerm.year]);
			return previousTerm;
		},

		/**
		 * Returns the next term based on the currently active date in the calendar
		 * @return {object} An object that contains all necessary term data: the term name, year, start and end dates.
		 */
		getNextTerm: function () {
			var currentTerm = this.getActiveTerm(),
				nextTerm = {
					year: Number(_.getYearFromDate(this.calendar.getActiveDate()))
				};

			switch (currentTerm) {
			case "michaelmas":
				nextTerm.term = "lent";
				nextTerm.year += 1;
				break;
			case "lent":
				nextTerm.term = "easter";
				break;
			case "easter":
				nextTerm.term = "michaelmas";
				break;
			default:
				nextTerm = this.getClosestRelativeTermFromDate(this.calendar.getActiveDate(), "next");
			}

			_.extend(nextTerm, this.terms[nextTerm.term][nextTerm.year]);
			return nextTerm;
		},

		/**
		 * Returns the closest term for a given date
		 * @param {object} date This is the date to search from
		 * @param {string} rel This is either "next" or "previous". Look forwards or
		 *		backwards from given date. Is "next" by default.
		 * @return {object} This returns an object with inside the term and year.
		 */
		getClosestRelativeTermFromDate: function (date, rel) {
			var activeTerm,
				dateIterator = rel === "previous" ? -(1000 * 60 * 60 * 24 * 30) : (1000 * 60 * 60 * 24 * 30);

			while (typeof activeTerm === "undefined") {
				activeTerm = this.getActiveTermForDate(date);
				date = new Date(date.valueOf() + dateIterator);
			}

			return {
				term: activeTerm,
				year: Number(_.getYearFromDate(date))
			};
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
		 * Moves the calendar to the previous week
		 */
		goToPreviousWeek: function () {
			this.calendar.goToDate(new Date(this.calendar.getActiveDate().valueOf() - (1000 * 60 * 60 * 24 * 7)));
		},

		/**
		 * Moves the calendar to the next term
		 */
		goToNextTerm: function () {
			var nextTerm = this.getRelativeTerm("next");
			this.calendar.goToDate(new Date(nextTerm.year, nextTerm.start.month - 1, nextTerm.start.day));
		},

		/**
		 * Moves the calendar to the previous term
		 */
		goToPreviousTerm: function () {
			var previousTerm = this.getRelativeTerm("previous");
			this.calendar.goToDate(new Date(previousTerm.year, previousTerm.start.month - 1, previousTerm.start.day));
		},

		/**
		 * Renders the dateSpinner to expose the correct active values
		 */
		render: function () {
			this.$(".js-value").text(_.capitalize(this.getValue()));
		}
	});

	return {
		FullCalendarView: FullCalendarView,
		DateSpinner: DateSpinner
	};

});