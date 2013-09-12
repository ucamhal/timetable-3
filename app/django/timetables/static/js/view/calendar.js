define([
    "jquery",
    "underscore",
    "backbone",
    "view/calendar-event-popup",
    "fullcalendar"
], function ($, _, Backbone, CalendarEventPopup) {
    "use strict";

    var FullCalendarView = Backbone.View.extend({
        initialize: function () {
            var self = this;
            _.bindAll(this, "onScroll");

            this.$el.fullCalendar({
                events: this.options.eventsFeed,
                ignoreTimezone: false, // Why is this true by default? WTF.
                allDaySlot: false,
                minTime: this.options.minTime || 7,
                maxTime: this.options.maxTime || 20,
                header: false,
                firstDay: this.options.firstDay || 1,
                columnFormat: {
                    week: "ddd dd/M"
                },
                eventRender: function (calEvent, $el, view) {
                    // Show the title and location in the event box if the
                    // active view is "agendaWeek"
                    if (view.name === "agendaWeek") {
                        $el.find(".fc-event-time").text(calEvent.title);
                        $el.find(".fc-event-title").text(calEvent.location);
                    }
                    $el.attr("aria-label", self.generateAuralEvent(calEvent))
                       .attr("role", "article");

                    self.$el.trigger("eventRender", [calEvent, $el, view]);
                },
                select: function () {
                }
            });

            this.setView(this.options.defaultView || "month");
            this.$(".fc-view-agendaWeek > div > div").on("scroll", this.onScroll);
            this.updateCalendarTableAriaHidden();
        },

        /**
         * Generates an accessible event string from a calEvent object.
         */
        generateAuralEvent: function (calEvent) {
            var dateString = $.fullCalendar.formatDate(calEvent.start, "dddd d MMMM"),

                timeStringFormat = "h:mmTT",
                // Generate readable date and time strings from the event start
                // and end dates.
                fromTimeString = $.fullCalendar.formatDate(calEvent.start, timeStringFormat),
                toTimeString = $.fullCalendar.formatDate(calEvent.end, timeStringFormat),
                eventTimeInfo = dateString + ", from " + fromTimeString + " to " + toTimeString,

                auralEvent = calEvent.title;

            // Type, location and lecturer aren't required fields on an event,
            // so we have to check whether they exist.
            if (calEvent.type) {
                auralEvent = calEvent.type + ": " + auralEvent;
            }

            if (calEvent.location) {
                auralEvent += ", at " + calEvent.location;
            }

            auralEvent += ". " + eventTimeInfo + ".";

            // calEvent.lecturer = Array
            if (calEvent.lecturer && calEvent.lecturer.length) {
                auralEvent += " Given by " + calEvent.lecturer.join(", ") + ".";
            }

            return auralEvent;
        },

        updateCalendarTableAriaHidden: function () {
            this.$el.fullCalendar("getView")
                .element
                .find("table")
                .attr("aria-hidden", true);
        },

        events: {
            "eventRender" : "onEventRender",
            "scroll" : "onScroll"
        },

        onScroll: function () {
            // Don't calculate the position if the popup isn't visible.
            if (!this.eventPopup || !this.eventPopup.shown) {
                return;
            }

            this.eventPopup.updatePosition();

            var popupPosition = this.eventPopup.getPosition(),
                calendarPosition = this.$el.offset();

            if (popupPosition.top < (calendarPosition.top + this.$("thead").height()) || popupPosition.top > calendarPosition.top + this.$el.height()) {
                this.eventPopup.toggle(false);
                this.$(".fc-event:focus").blur();
            }
        },

        refresh: function () {
            this.$el.fullCalendar("refetchEvents");
        },

        onEventRender: function (renderEvent, calEvent, $el, view) {
            var self = this;

            $el.attr("tabindex", 0);
            $el.on("focusin", function (focusEvent) {
                self.onEventFocus(calEvent, $el, view, this, focusEvent);
            });
        },

        hide: function () {
            this.$el.hide();
        },

        show: function () {
            this.$el.show();
            this.$el.fullCalendar("render");
        },

        /**
         * Eventhandler that is triggered when an event on the calendar
         *        has been focussed
         */
        onEventFocus: function (calEvent, $el, view, target) {
            this.resetZIndexForAllEvents();
            $(target).css("zIndex", 9);

            // Create an instance of the CalendarEventPopup class if it hasn't
            // been created yet.
            if (!this.eventPopup) {
                this.createEventPopup();
            }

            this.eventPopup.setModelFromCalEvent(calEvent);
            this.eventPopup.render();
            this.eventPopup.toggle(true, $el);
        },

        /**
         * Creates an instance of the CalendarEventPopup class and saves it in
         * this.eventPopup
         */
        createEventPopup: function () {
            this.eventPopup = new CalendarEventPopup({
                $context: this.$el
            });
            $("body").append(this.eventPopup.$el);
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
            if (this.eventPopup) {
                this.eventPopup.toggle(false);
            }
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
            this.$el.removeClass("view-agendaWeek view-month");
            this.$el.addClass("view-" + view);
            this.$el.fullCalendar("changeView", view);
            this.updateCalendarTableAriaHidden();
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

    return FullCalendarView;
});
