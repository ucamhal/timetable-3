define([
    "jquery",
    "underscore",
    "backbone",
    "util/underscore-mixins",
    "fullcalendar"
], function ($, _, Backbone) {
    "use strict";

    var CalendarModel = Backbone.Model.extend({
        day: 1000 * 60 * 60 * 24,
        week: 1000 * 60 * 60 * 24 * 7,

        initialize: function () {
            this.on("change:activeDate", this.onActiveDateChange);
        },

        defaults: {
            activeWeek: false,
            activeMonth: false,
            activeTerm: false
        },

        onActiveDateChange: function () {
            var date = this.getActiveDate();
            this.set({
                activeTerm: this.getTermForDate(date),
                activeWeek: this.getTermWeekForDate(date),
                activeMonth: this.getMonthForDate(date),
                activeMonthTerm: this.getTermForMonth(date)
            });
        },

        /**
         * Sets the active date to the provided date within the defined start
         * and end bounds.
         */
        setActiveDate: function (date) {
            this.set("activeDate", this.putDateWithinBoundaries(date));
        },

        /**
         * Returns the active date.
         */
        getActiveDate: function () {
            return new Date(this.get("activeDate").valueOf());
        },

        /**
         * Returns the active week.
         */
        getActiveWeek: function () {
            return this.get("activeWeek");
        },

        /**
         * Returns the active month.
         */
        getActiveMonth: function () {
            return this.get("activeMonth");
        },

        /**
         * Returns the name attribute of the provided term object.
         */
        getTermName: function (term) {
            if (!term) {
                return;
            }
            return _.capitalize(term.name);
        },

        getActiveMonthTermName: function () {
            return this.getTermName(this.get("activeMonthTerm"));
        },

        /**
         * Returns the term name from the currently active term.
         */
        getActiveTermName: function () {
            return this.getTermName(this.get("activeTerm"));
        },

        /**
         * Returns the closest date possible for the provided date within the
         * defined calendar start and end boundaries.
         */
        putDateWithinBoundaries: function (date) {
            var calendarEnd = this.get("end"),
                calendarStart = this.get("start");

            if (date > calendarEnd) {
                date = calendarEnd;
            } else if (date < calendarStart) {
                date = calendarStart;
            }

            return date;
        },

        /**
         * Returns true/false based on whether the provided date is within the
         * calendar start and end boundaries.
         */
        isDateWithinBoundaries: function (date) {
            var calendarEnd = this.get("end"),
                calendarStart = this.get("start");

            return (date <= calendarEnd && date >= calendarStart);
        },

        /**
         * Checks whether the cambridge week that the provided date falls in is
         * within the start and end boundaries of the calendar (also returns
         * true when a boundary falls within the cambridge week).
         */
        isCambridgeWeekWithinBoundaries: function (date) {
            var calendarStartWeek = this.getCambridgeWeekStartForDate(this.get("start")),
                calendarEndWeek = this.getCambridgeWeekStartForDate(this.get("end")),
                dateWeek = this.getCambridgeWeekStartForDate(date);

            return (dateWeek <= calendarEndWeek && dateWeek >= calendarStartWeek);
        },

        /**
         * Checks whether the month that the provided date falls in is within
         * the start and end boundaries of the calendar (also returns true when
         * a boundary falls within the the month).
         */
        isMonthWithinBoundaries: function (date) {
            var calendarEndMonth = this.getMonthStartForDate(this.get("end")),
                calendarStartMonth = this.getMonthStartForDate(this.get("start")),
                dateMonth = this.getMonthStartForDate(date);

            return (dateMonth <= calendarEndMonth && dateMonth >= calendarStartMonth);
        },

        /**
         * Moves the active date to the closest previous term. Keeps the week
         * offset in place.
         */
        goToPrevTerm: function () {
            var activeWeek = this.get("activeWeek") - 1 || 0,
                prevTerm = this.getPrevTermForDate(this.getActiveDate()),
                termDate;

            if (prevTerm) {
                // Keep the week offset
                termDate = new Date(prevTerm.start.valueOf());
                termDate.setDate(termDate.getDate() + (activeWeek * 7));
                this.setActiveDate(termDate);
            }
        },

        /**
         * Moves the active date to the closest next term. Keeps the week offset
         * in place.
         */
        goToNextTerm: function () {
            var activeWeek = this.get("activeWeek") - 1 || 0,
                nextTerm = this.getNextTermForDate(this.getActiveDate()),
                termDate;

            if (nextTerm) {
                // Keep the week offset
                termDate = new Date(nextTerm.start.valueOf());
                termDate.setDate(termDate.getDate() + (activeWeek * 7));
                this.setActiveDate(termDate);
            }
        },

        /**
         * Moves the calendar to the first found Thursday in the previous month.
         */
        goToPrevMonthFirstThursday: function () {
            var prevMonth = this.moveDateToPrevMonth(this.getActiveDate());
            if (prevMonth.getDay() !== 4) {
                prevMonth = this.moveDateToNextCambridgeWeek(prevMonth);
            }
            this.setActiveDate(prevMonth);
        },

        /**
         * Moves the calendar to the first found Thursday in the next month.
         */
        goToNextMonthFirstThursday: function () {
            var nextMonth = this.moveDateToNextMonth(this.getActiveDate());
            if (nextMonth.getDay() !== 4) {
                nextMonth = this.moveDateToNextCambridgeWeek(nextMonth);
            }
            this.setActiveDate(nextMonth);
        },

        /**
         * Moves the active date backwards one week.
         */
        goToPrevWeek: function () {
            this.setActiveDate(this.moveDateToPrevWeek(this.getActiveDate()));
        },

        /**
         * Moves the active date forwards one week.
         */
        goToNextWeek: function () {
            this.setActiveDate(this.moveDateToNextWeek(this.getActiveDate()));
        },

        /**
         * Moves the active date to the start of the previous cambridge week.
         */
        goToPrevCambridgeWeek: function () {
            this.setActiveDate(this.moveDateToPrevCambridgeWeek(this.getActiveDate()));
        },

        /**
         * Moves the active date to the start of the next cambridge week.
         */
        goToNextCambridgeWeek: function () {
            this.setActiveDate(this.moveDateToNextCambridgeWeek(this.getActiveDate()));
        },

        /**
         * Moves the active date to the start of the cambridge week.
         */
        goToCambridgeWeekStart: function () {
            this.setActiveDate(this.getCambridgeWeekStartForDate(this.getActiveDate()));
        },

        /**
         * Returns the start of the month date for the provided date.
         */
        getMonthStartForDate: function (date) {
            return new Date(date.getFullYear(), date.getMonth(), 1);
        },

        /**
         * Finds the term in which the provided date takes place. Returns
         * undefined if no term is found.
         */
        getTermForDate: function (date) {
            var self = this,
                terms = this.get("terms"),
                term;

            // Iterate over all the terms.
            _.each(terms, function (singleTerm) {
                // Check whether the date falls within the term.
                if (date >= singleTerm.start && date <= self.getTermEndDate(singleTerm)) {
                    term = singleTerm;
                }
            });

            return term;
        },

        /**
         * Finds the term only based on the month of a provided date. If the any
         * date of a term falls within the month, it returns that term.
         */
        getTermForMonth: function (date) {
            var self = this,
                terms = this.get("terms"),
                monthStart = this.getMonthStartForDate(date),
                term;
            _.each(terms, function (singleTerm) {
                var termMonthStart = self.getMonthStartForDate(singleTerm.start),
                    termMonthEnd = self.getMonthStartForDate(self.getTermEndDate(singleTerm));
                if (monthStart >= termMonthStart && monthStart <= termMonthEnd) {
                    term = singleTerm;
                }
            });
            return term;
        },

        /**
         * Returns the term week number in which the provided date takes place.
         */
        getTermWeekForDate: function (date) {
            var term = this.getTermForDate(date),
                week;
            if (term) {
                // Calculate the week number.
                week = Math.floor((date - term.start) / this.week);
            }

            return week + 1;
        },

        /**
         * Calculates and returns the end date of a term.
         */
        getTermEndDate: function (term) {
            // Add 8 weeks to the term start date.
            var end = new Date(term.start.valueOf());
            end.setDate(end.getDate() + (8 * 7 - 1));
            return end;
        },

        /**
         * Returns the full month name in which the provided date takes place.
         */
        getMonthForDate: function (date) {
            return $.fullCalendar.formatDate(date, "MMMM");
        },

        /**
         * Returns the first next possible term for a given date.
         */
        getNextTermForDate: function (date) {
            var activeTerm = this.getTermForDate(date),
                terms = _.without(this.get("terms"), activeTerm),
                nextTerm;

            // Iterate over all the terms.
            _.each(terms, function (term) {
                // Check whether the term is in the future of the provided date.
                // Also check whether the found term is closer in time than the
                // previously found one.
                if (term.start > date && (!nextTerm || nextTerm.start > term.start)) {
                    nextTerm = term;
                }
            });

            return nextTerm;
        },

        /**
         * Moves a provided date to the previous thursday.
         */
        getCambridgeWeekStartForDate: function (date) {
            var dateDay = date.getDay(),
                weekStart = new Date(date.valueOf());

            // Just return the date if the date day is already on a Thursday.
            if (dateDay !== 4) {
                // Move the day of the week to the previous Thursday.
                weekStart.setDate(weekStart.getDate() - (dateDay >= 4 ? (dateDay - 4) : (7 - (4 - dateDay))));
            }
            return weekStart;
        },

        /**
         * Moves a provided date to the next month.
         */
        moveDateToNextMonth: function (date) {
            var monthStart = this.getMonthStartForDate(date);
            monthStart.setMonth(monthStart.getMonth() + 1);
            return monthStart;
        },

        /**
         * Moves a provided date to the previous month.
         */
        moveDateToPrevMonth: function (date) {
            var monthStart = this.getMonthStartForDate(date);
            monthStart.setMonth(monthStart.getMonth() - 1);
            return monthStart;
        },

        /**
         * Moves the provided date to the start of the next cambridge week.
         */
        moveDateToNextCambridgeWeek: function (date) {
            var weekStart = this.getCambridgeWeekStartForDate(date);
            return this.moveDateToNextWeek(weekStart);
        },

        /**
         * Moves the provided date to the start of the previous cambridge week.
         */
        moveDateToPrevCambridgeWeek: function (date) {
            var weekStart = this.getCambridgeWeekStartForDate(date);
            return this.moveDateToPrevWeek(weekStart);
        },

        /**
         * Moves the provided date one week forwards.
         */
        moveDateToNextWeek: function (date) {
            var newDate = new Date(date.valueOf());
            newDate.setDate(newDate.getDate() + 7);
            return newDate;
        },

        /**
         * Moves the provided date one week back.
         */
        moveDateToPrevWeek: function (date) {
            var newDate = new Date(date);
            newDate.setDate(newDate.getDate() - 7);
            return newDate;
        },

        /**
         * Returns the first previous possible term for a given date.
         */
        getPrevTermForDate: function (date) {
            var activeTerm = this.getTermForDate(date),
                terms = _.without(this.get("terms"), activeTerm),
                previousTerm;

            // Iterate over all the terms.
            _.each(terms, function (term) {
                // Check whether the term is in the past of the provided date.
                // Also check whether the found term is closer in time than the
                // previously found one.
                if (term.start < date && (!previousTerm || term.start > previousTerm.start)) {
                    previousTerm = term;
                }
            });

            return previousTerm;
        }
    });

    return CalendarModel;
});
