define([
    "jquery",
    "underscore",
    "backbone",
    "fullcalendar",
    "util/underscore-mixins"
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
            this.shown = false;
            this.$context = opts.$context;
            this.$el.appendTo("body");
        },

        /**
         * Event handler when a close button has been clicked. Hides the popup 
         * element.
         */
        onClose: function (event) {
            this.toggle(false);
            event.preventDefault();
        },

        /**
         * Updates the element markup to display the current values in the 
         * eventData property
         */
        render: function () {
            this.$(".js-course-title").text(this.eventData.title || "")
                .removeClass()
                .addClass("js-course-title");
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
                seriesId: parseInt(calEvent.eventSourceId, 10)
            };
        },

        /**
         * This updates the position of the popup element
         */
        updatePosition: function () {
            if (this.$context instanceof $) {
                var position = {
                        top: this.$context.offset().top - (this.$el.outerHeight() / 2
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
            };
        },

        /**
         * Toggles the event popup.
         * Can implicitly show/hide by giving true/false along with the context.
         */
        toggle: function (show, $context) {
            show = typeof show === undefined ? !this.shown : show;
            if (show !== this.shown || ($context !== this.$context && show === true)) {
                if (show) {
                    this.$el.show();
                    this.$context = $context;
                    this.updatePosition();
                } else {
                    this.$el.hide();
                    this.$context = undefined;
                }

                this.shown = show;
            }
        }
    });

    var FullCalendarView = Backbone.View.extend({

        initialize: function () {
            var self = this;

            _.bindAll(this, "onScroll");

            this.eventPopup = new CalendarEventPopup({
                el: ".js-calendar-popup",
                $context: this.$el
            });

            this.$el.fullCalendar({
                defaultView: this.options.defaultView || "month",
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

                    self.$el.trigger("eventRender", [calEvent, $el, view]);
                },
                select: function () {
                }
            });

            this.$(".fc-view-agendaWeek > div > div").on("scroll", this.onScroll);
        },

        events: {
            "eventRender" : "onEventRender",
            "scroll" : "onScroll"
        },

        onScroll: function () {
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

            $el.attr("tabindex", this.$(".fc-event").index($el));
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
            this.eventPopup.setEventDataFromCalEvent(calEvent);
            this.eventPopup.render();
            this.eventPopup.toggle(true, $el);
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
            this.eventPopup.toggle(false);
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
        initialize: function () {
            _.bindAll(this);

            this.model = new Backbone.Model({
                next: true,
                prev: true,
                value: undefined
            });

            this.$label = this.$(".js-value");
            this.bindEvents();
        },

        set: function (data) {
            this.model.set(data);
        },

        bindEvents: function () {
            this.listenTo(this.model, "change", this.render);
        },

        render: function () {
            this.updateLabel();
            this.updateButtons();
        },

        updateLabel: function () {
            this.$label.text(this.model.get("value"));
        },

        updateButtons: function () {
            this.$(".js-prev").toggleClass("disabled", !this.model.get("prev"));
            this.$(".js-next").toggleClass("disabled", !this.model.get("next"));
        },

        events: {
            "click .js-prev": "onClickPrevious",
            "click .js-next": "onClickNext"
        },

        onClickPrevious: function (event) {
            if (this.model.get("prev")) {
                this.trigger("prev");
            }
            event.preventDefault();
        },

        onClickNext: function (event) {
            if (this.model.get("next")) {
                this.trigger("next");
            }
            event.preventDefault();
        }
    });

    return {
        FullCalendarView: FullCalendarView,
        DateSpinner: DateSpinner
    };
});
