define([
    "jquery",
    "underscore",
    "backbone",
    "model/calendar-event-popup",
    "util/timetable-events",
    "util/underscore-mixins"
], function ($, _, Backbone, CalendarEventPopupModel, timetableEvents) {
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

        attributes: {
            "aria-hidden": true,
            "class": "alert alert-block clearfix calendarEventInfo"
        },

        template: _.template($("#js-templ-calendar-event-popup").html()),

        tagName: "div",

        initialize: function (opts) {
            _.bindAll(this);

            this.positionMutators = _.defaults({
                leftOffset: opts.leftOffset,
                topOffset: opts.topOffset,
                contentWidth: opts.contentWidth
            }, this.positionMutators);

            this.model = new CalendarEventPopupModel();
            this.shown = false;
            this.$context = opts.$context;
            this.bindEvents();
        },

        bindEvents: function () {
            var throttledOnModelSeriesIdChange = _.throttle(this.onModelSeriesIdChange, 200);
            this.listenTo(this.model, "change:seriesId", throttledOnModelSeriesIdChange);
            this.listenTo(this.model, "change", this.render);
        },

        onModelSeriesIdChange: function (model) {
            model.set({
                subject: ""
            }).updateSubjectTitle();
        },

        /**
         * Hides (doesn't remove) the popup element.
         */
        onClose: function (event) {
            this.toggle(false);
            event.preventDefault();
        },

        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            this.updatePosition();
        },

        /**
         * Updates the model from a provided fullCalendar CalEvent
         */
        setModelFromCalEvent: function (calEvent) {
            this.model.set({
                id: calEvent.djid,
                title: calEvent.title,
                datePattern: _.getFullDayFromDate(calEvent._start) + " " + _.getTwelveHourTimeFromDate(calEvent._start),
                location: calEvent.location,
                lecturers: calEvent.lecturer.toString(),
                type: calEvent.type,
                seriesId: parseInt(calEvent.eventSourceId, 10)
            });
        },

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
                    timetableEvents.trigger("click_event");
                } else {
                    this.$el.hide();
                    this.$context = undefined;
                }

                this.shown = show;
            }
        }
    });

    return CalendarEventPopup;
});
