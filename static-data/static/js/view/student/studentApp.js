define([
	"jquery",
	"underscore",
	"view/base/baseApp",
	"view/student/components/studentInputArea",
	"view/student/components/studentResults",
	"view/student/components/studentCalendar",
	"control/hashController",
	"util/page",
	"bootstrap",
	"bootstrapTimePicker",
	"bootstrapDatePicker"
], function ($, _, BaseApplication, StudentInputArea, StudentResults, StudentCalendar, HashController, page) {
	"use strict";

	var StudentApplication = function () {
		this.baseInitialize();
		this.initialize();
	};

	_.extend(StudentApplication.prototype, BaseApplication.prototype);
	_.extend(StudentApplication.prototype, {
		initialize: function () {

			var self = this;

			_.defaults(this, {
				results: new StudentResults({
					selector: "div#results"
				}),
				calendar: new StudentCalendar({
					selector: "div#calendarHolder",
                    headingSelector: "div#calendarHeading",
                    contentSelector: "div#calendar"
				}),
				inputArea: new StudentInputArea({
					selector: "div#inputArea"
				})
			});

			this.hashController = new HashController({
				resultsView: this.results,
				calendarView: this.calendar,
				inputAreaView: this.inputArea
			});

			_.addEventListener(this.results.$el, "timetableChanged", function (event) {
				self.calendar.content.refresh();
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

	return StudentApplication;
});
