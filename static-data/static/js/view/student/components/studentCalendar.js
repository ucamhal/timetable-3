define([
	"jquery",
	"underscore",
	"view/base/components/baseCalendar",
	"view/student/components/calendarComponents/studentCalendarHeading",
	"view/student/components/calendarComponents/studentCalendarContent"
], function ($, _, BaseCalendar, StudentCalendarHeading, StudentCalendarContent) {
	"use strict";

	var StudentCalendar = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(StudentCalendar.prototype, BaseCalendar.prototype);
	_.extend(StudentCalendar.prototype, {
		initialize: function () {
			_.defaults(this, {
				content: new StudentCalendarContent({
					selector: this.contentSelector,
					parent: this
				}),
				heading: new StudentCalendarHeading({
					selector: this.headingSelector,
					parent: this
				})
			});
		}
	});

	return StudentCalendar;
});