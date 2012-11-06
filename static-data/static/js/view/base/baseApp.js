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

				dispatchEvent: function (from, eventName) {
					from.trigger(eventName);
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
			})

			_.defaults(this, {

				hashController: new HashController({
					resultsView: this.results,
					calendarView: this.calendar,
					inputAreaView: this.inputArea
				})

			});

			_.addEventListener(this.results.$el, "timetableChanged", function (event) {
				self.calendar.content.refresh();
			});

			$("a[href=\"#\"]").live("click", function (event) {
				event.preventDefault();
			});

			$(window).resize(function (e) {
				var maxWidth = $(window).width() - 200;

				if(maxWidth < 960) {
					maxWidth = 960;
				} else if (maxWidth > 1400) {
					maxWidth = 1400;
				}

				$("#inputArea > div").width(maxWidth);
				$("#uniLogo").width(maxWidth);
				$("#content").width(maxWidth);
				$("#actionsContainer").width(maxWidth);

				self.results.resize();
				self.calendar.resize({
					height: self.results.$el.height(),
					width: maxWidth - self.results.$el.outerWidth() - 50
				});

			});
			$(window).trigger("resize").trigger("hashchange");
		}
	});

	return BaseApplication;


});