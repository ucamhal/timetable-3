define([
    "jquery",
    "underscore",
    "fullcalendar"
],function ($, _) {
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
        },

        /**
         * Returns a version of the function f which delays calls to f using
         * _.defer. Any return value of f will be lost/ignored.
         */
        deferred: function (f) {
            // The wrapped function which will defer the call to f,
            // maintaining the origional this context and arguments.
            return function() {
                var _this = this;
                var _arguments = arguments;
                _.defer(function() {
                    f.apply(_this, _arguments);
                })
            }
        }
    });

    return _;
});
