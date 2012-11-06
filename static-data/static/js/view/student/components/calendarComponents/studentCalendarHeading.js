define(["jquery", "underscore", "view/base/components/calendarComponents/baseCalendarHeading"], function ($, _, BaseCalendarHeading) {
	"use strict";

	var StudentCalendarHeading = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(StudentCalendarHeading.prototype, BaseCalendarHeading.prototype);
	_.extend(StudentCalendarHeading.prototype, {
		initialize: function () {
		}
	});

	return StudentCalendarHeading;
});