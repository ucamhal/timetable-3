define([
    "jquery",
    "underscore",
    "backbone",
    "fullcalendar"
], function ($, _, Backbone) {
    "use strict";

    var CalendarEventPopup = Backbone.View.extend({

        events: {
            "click .js-close" : "onClose"
        },

        positionMutators: {
            leftOffset: 10,
            topOffset: 0,
            contentWidth: 960
        },

        initialize: function (opts) {
            this.positionMutators.leftOffset = opts.leftOffset || this.positionMutators.leftOffset;
            this.positionMutators.topOffset = opts.topOffset || this.positionMutators.topOffset;
            this.positionMutators.contentWidth = opts.contentWidth || this.positionMutators.contentWidth;

            this.$el.appendTo("body");
        },

        /**
         * Event handler when a close button has been clicked. Hides the popup 
         * element.
         */
        onClose: function (event) {
            this.hide();
            event.preventDefault();
        },

        /**
         * Updates the element markup to display the current values in the 
         * eventData property
         */
        render: function () {
            this.$(".js-course-title").text(this.eventData.title || "")
                .removeClass()
                .addClass("js-course-title")
                .addClass(typeof this.eventData.type !== "undefined" ?
                        "event-type-" + this.eventData.type
                        : "");
            this.$(".js-course-date-pattern").text(
                this.eventData.datePattern || ""
            );
            this.$(".js-course-location").text(this.eventData.location || "");
            this.$(".js-course-lecturer").text(this.eventData.lecturers || "");
            this.$(".js-edit").attr("href", this.$(".js-edit").data("base-url")
                + "#expand=" + this.eventData.seriesId
                + "&highlight=" + this.eventData.id);
        },

        /**
         * Updates the eventData property from a fullCalendar CalEvent
         * @param {object} calEvent The fullCalendar calEvent object.
         */
        setEventDataFromCalEvent: function (calEvent) {
            this.eventData = {
                id: calEvent.djid,
                title: calEvent.title,
                datePattern: _.getFullDayFromDate(calEvent._start) + " "
                    + _.getTwelveHourTimeFromDate(calEvent._start),
                location: calEvent.location,
                lecturers: calEvent.lecturer.toString(),
                type: calEvent.type,
                seriesId: parseInt(calEvent.eventSourceId)
            };

            console.log("bla");
        },

        /**
         * This updates the position of the popup element
         */
        updatePosition: function () {
            if (typeof this.$context !== "undefined") {
                var position = {
                        top: this.$context.offset().top
                            - (this.$el.outerHeight() / 2
                            - this.$context.outerHeight() / 2)
                            + this.positionMutators.topOffset,
                        left: this.$context.offset().left
                            + this.$context.outerWidth()
                            + this.positionMutators.leftOffset
                    },
                    contentBoundary = this.positionMutators.contentWidth
                        + Math.max(($(window).width()
                        - this.positionMutators.contentWidth) / 2, 0),
                    isOutsideBoundary = position.left + this.$el.outerWidth()
                        >= contentBoundary;

                if (isOutsideBoundary === true) {
                    position.left = (this.$context.offset().left
                        - this.$el.outerWidth())
                        - this.positionMutators.leftOffset;
                }

                this.$el.toggleClass("js-positioned-left", isOutsideBoundary);
                this.$el.css(position);
            }
        },

        getPosition: function () {
            return {
                top: this.$el.offset().top + this.$el.outerHeight() / 2,
                left: this.$el.offset().left
            }
        },

        /**
         * Function that makes the popup element visible
         * @param {object} $context The element the popup need to be relatively
         *        positioned to
         * @param {boolean} animated Set to true of popup has to be made visible
         *        using an animation (fade). Defaults to false.
         * @param {number} duration The duration of the animation in
         *        milliseconds. Defaults to 200ms.
         */
        show: function ($context, animated, duration) {
            this.$context = $context;
            this.updatePosition();

            animated = animated === true ? true : false;
            duration = duration || 200;

            if (animated === true) {
                this.$el.fadeIn(duration);
            } else {
                this.$el.show();
            }
        },

        /**
         * Function that hides the popup element
         * @param {boolean} animated Set to true of popup has to be hidden using
         *        an animation (fade). Defaults to false.
         * @param {number} duration The duration of the animation in
         *        milliseconds. Defaults to 200ms.
         */
        hide: function (animated, duration) {
            animated = animated === true ? true : false;
            duration = duration || 200;

            if (animated === true) {
                this.$el.fadeOut(duration);
            } else {
                this.$el.hide();
            }

            this.$context = undefined;
        }
    });

    var FullCalendarView = Backbone.View.extend({

        initialize: function (opts) {
            var self = this;

            _.bindAll(this, "onScroll");

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
                },
                eventRender: function (calEvent, $el, view) {
                    self.$el.trigger("eventRender", [calEvent, $el, view]);
                },
                select: function () {
                    console.log("event select");
                }
            });

            this.$(".fc-view-agendaWeek > div > div").on("scroll", this.onScroll);
        },

        events: {
            "eventRender" : "onEventRender",
            "scroll" : "onScroll",
        },

        onScroll: function () {
            this.eventPopup.updatePosition();

            var popupPosition = this.eventPopup.getPosition(),
                calendarPosition = this.$el.offset();

            if (popupPosition.top < (calendarPosition.top + this.$("thead").height()) || popupPosition.top > calendarPosition.top + this.$el.height()) {
                this.eventPopup.hide();
                this.$(".fc-event:focus").blur();
            }
        },

        refresh: function () {
            this.$el.fullCalendar("refetchEvents");
        },
        
        onEventRender: function (event, calEvent, $el, view) {
            var self = this;
            
            $el.attr("tabindex", this.$(".fc-event").index($el));
            $el.on("focusin", function () {
                self.onEventFocus(calEvent, $el, view, this);
            });
        },

        hide: function () {
            this.$el.hide();
        },

        show: function () {
            this.$el.show();
            this.$el.fullCalendar("render");
        },

        eventPopup: new CalendarEventPopup({
            el: ".js-calendar-popup"
        }),

        /**
         * Eventhandler that is triggered when an event on the calendar
         *        has been focussed
         */
        onEventFocus: function (calEvent, jsEvent, view, target) {
            this.resetZIndexForAllEvents();
            $(target).css("zIndex", 9);
            this.eventPopup.setEventDataFromCalEvent(calEvent);
            this.eventPopup.render();
            this.eventPopup.show($(target));
        },

        /**
         * Resets the z-index css property for each event to 8
         *        (fullCalendar default)
         */
        resetZIndexForAllEvents: function () {
            this.$(".fc-event").css("zIndex", 8);
        },

        /**
         * Hides the event popup and clears its context
         */
        resetEventPopup: function () {
            this.eventPopup.hide();
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
            this.resetEventPopup();
            this.$el.fullCalendar("changeView", view);
        },

        /**
         * Gets the active view object from fullCalendar
         *        (http://arshaw.com/fullcalendar/docs/views/getView/)
         * @return {object} Returns a fullCalendar View object.
         */
        getView: function () {
            return this.$el.fullCalendar("getView");
        },

        getViewName: function () {
            return this.getView().name;
        },

        /**
         * Moves the calendar to the specified date. Will manipulate the date to
         *        always go to the start of the week (Thursday)
         * @param {object} date The date the calendar has to move to.
         */
        goToDate: function (date) {
            this.resetEventPopup();
            this.$el.fullCalendar("gotoDate", date);
        },

        setHeight: function (height) {
            this.$el.fullCalendar("option", "height", height);
            this.$el.height(height);
        },

        setWidth: function (width) {
            this.$el.width(width);
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
         * Updates the activeTermData object with new values based on the active
         *        calendar date
         */
        updateActiveTermData: function () {
            if (this.type === "term" && this.calendar.getViewName() === "month") {
                this.activeTermData = this.getTermDataForMonth(this.calendar.getActiveDate());
            } else {
                this.activeTermData = this.getTermDataForDate(this.calendar.getActiveDate());
            }
        },

        /**
         * Returns the value of the datespinner
         * @return {string} The current value of the dateSpinner
         *        (dependant on the type)
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
            case "month":
                value = this.getActiveMonthString();
            }
            return value;
        },

        /**
         * Returns the currently active month e.g. January
         * @return {string} The currently active month
         */
        getActiveMonthString: function () {
            return $.fullCalendar.formatDate(this.calendar.getActiveDate(), "MMMM yyyy");
        },

        /**
         * Returns the currently active week withing the currently active term
         *        in a nice string format e.g. Week 3
         * @return {string} A string representing the currently active week
         *        within the active term
         */
        getActiveWeekString: function () {
            var activeWeekString = "Outside term";
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
            var activeTermString = "No active term",
                termData;
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
            case "month":
                this.goToPreviousMonth();
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
         * Moves the calendar back one month
         */
        goToPreviousMonth: function () {
            var activeDate = this.calendar.getActiveDate();
            this.calendar.goToDate(new Date(activeDate.getFullYear(), activeDate.getMonth() - 1, 1));
        },

        /**
         * Moves the calendar to the previous term
         */
        goToPreviousTerm: function () {
            if (typeof this.activeTermData !== "undefined") {
                this.calendar.goToDate(this.getRelativeTermDateFromActiveTerm("backwards", this.calendar.getViewName() === "month"));
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
            case "month":
                this.goToNextMonth();
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
         * Moves the calendar forwards on month
         */
        goToNextMonth: function () {
            var activeDate = this.calendar.getActiveDate();
            this.calendar.goToDate(new Date(activeDate.getFullYear(), activeDate.getMonth() + 1, 1));
        },

        /**
         * Moves the calendar to the next term
         */
        goToNextTerm: function () {
            if (typeof this.activeTermData !== "undefined") {
                this.calendar.goToDate(this.getRelativeTermDateFromActiveTerm("forwards", this.calendar.getViewName() === "month"));
            } else {
                this.calendar.goToDate(this.getRelativeTermDateFromDate(this.calendar.getActiveDate(), "forwards"));
            }
        },

        getTermDataForMonth: function (date) {
            var month = date.getMonth(),
                terms = this.getTermsForDateYear(date),
                activeTermData,
                selectedMonth,
                self = this;

            _.each(terms, function (termData, termName) {
                if (typeof activeTermData === "undefined") {
                    _.each(termData, function (weekStartDate, weekNr) {
                        selectedMonth = self.parseDate(weekStartDate).getMonth();
                        if (selectedMonth === month) {
                            activeTermData = {
                                week: weekNr,
                                date: self.parseDate(weekStartDate),
                                term: termName
                            }
                        }
                    });
                }
            });

            return activeTermData;
        },

        /**
         * Returns term data for the week the date is in.
         * @param {object} date This is the date that will be used to find the
         *        correct term data.
         * @param {string} rel Look forwards or backwards from date if date is
         *        not a Thursday. (if date is not a thursday it moves to the
         *        closest Thursday using the direction defined here)
         * @return {object} Object containing term data of the term the date
         *        falls in.
         */
        getTermDataForDate: function (date, rel) {
            var self = this,
                terms = this.getTermsForDateYear(date),
                direction = rel || "backwards",
                activeTermData,
                activeDate = this.getClosestThursdayFromDate(date, direction),

                activeYear = activeDate.getFullYear(),
                activeMonth = (String(activeDate.getMonth() + 1).length === 1 ? "0" + (activeDate.getMonth() + 1) : activeDate.getMonth() + 1),
                activeDay = (String(activeDate.getDate()).length === 1 ? "0" + activeDate.getDate() : activeDate.getDate()),

                activeDateString = activeYear + "-" + activeMonth + "-" + activeDay;

            _.each(terms, function (termData, termName) {
                if (typeof activeTermData === "undefined") {
                    _.each(termData, function (weekStartDate, weekNr) {
                        if (weekStartDate === activeDateString) {
                            activeTermData = {
                                week: weekNr,
                                date: self.parseDate(weekStartDate),
                                term: termName
                            };
                        }
                    });
                }
            });

            return activeTermData;
        },

        /*
         * Finds first possible next or previous date that falls inside a term.
         *        Starts searching from the given date.
         * @param {object} data The date to start searching from.
         * @param {string} rel The direction to look, forwards by default.
         * @return {object} The closest date relative to the provided date that
         *        falls inside a term.
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

            return termData ? termData.date : this.calendar.getActiveDate();
        },
        
        /**
         * Converts a date string to a js Date object. Expects string format to be yyyy-mm-dd
         * @param {string} dateString The date string to be converted.
         * @return {object} The string as a Date object.
         */
        parseDate: function (dateString) {
            var parts = dateString.match(/(\d+)/g);
            return new Date(parts[0], parts[1] - 1, parts[2]);
        },

        /**
         * Gets the date for the next or previous term based on the currently
         *        active term. Remembers the currently active week.
         * @param {string} rel The direction to go, either forwards of
         *        backwards, forwards by default.
         * @return {object} Date object that falls within next or previous term.
         */
        getRelativeTermDateFromActiveTerm: function (rel, forceFirstWeek) {
            var activeYear = this.getAcademicStartYearFromDate(this.activeTermData.date),
                termDate,
                direction = rel || "forwards",
                weekNr = forceFirstWeek ? 1 : this.activeTermData.week;

            switch (this.activeTermData.term) {
            case "michaelmas":
                if (direction === "forwards" && this.terms[activeYear]) {
                    termDate = this.terms[activeYear].lent[weekNr];
                } else if (this.terms[activeYear - 1]) {
                    termDate = this.terms[activeYear - 1].easter[weekNr];
                }
                break;
            case "lent":
                if (this.terms[activeYear]) {
                    if (direction === "forwards") {
                        termDate = this.terms[activeYear].easter[weekNr];
                    } else {
                        termDate = this.terms[activeYear].michaelmas[weekNr];
                    }
                }
                break;
            case "easter":
                if (direction === "forwards" && this.terms[activeYear + 1]) {
                    termDate = this.terms[activeYear + 1].michaelmas[weekNr];
                } else if(this.terms[activeYear]) {
                    termDate = this.terms[activeYear].lent[weekNr];
                }
                break;
            }

            return termDate ? this.parseDate(termDate) : this.calendar.getActiveDate();
        },

        /**
         * Returns the closest thursday from a given date
         * @param {object} date This is the date to search from.
         * @param {string} rel "next" or "previous", "previous" by default.
         *        Determines whether to look forwards or backwards from given date
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
            return date.getMonth() < 9 ? date.getFullYear() - 1 : date.getFullYear();
        }
    });

    return {
        FullCalendarView: FullCalendarView,
        DateSpinner: DateSpinner
    };

});
