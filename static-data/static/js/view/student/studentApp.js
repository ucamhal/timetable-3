define([
	"jquery",
	"underscore",
	"view/base/BaseApp",
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
		this.initialize();
		this.baseInitialize();
	};

	_.extend(StudentApplication.prototype, BaseApplication.prototype);
	_.extend(StudentApplication.prototype, {
		initialize: function () {

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
			
		}
	});

	return StudentApplication;
});
