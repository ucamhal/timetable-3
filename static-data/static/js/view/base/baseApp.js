define([
	"jquery",
	"underscore",
	"util/page",
	"control/hashController",
	"bootstrap",
	"fullcalendar"
], function ($, _, page, HashController) {
	"use strict";

	var BaseApplication = function () {

	}

	_.extend(BaseApplication.prototype, {
		baseInitialize: function () {

			var self = this;

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
				}
			});

			$("a[href=\"#\"]").live("click", function (event) {
				event.preventDefault();
			});
		}
	});

	return BaseApplication;


});