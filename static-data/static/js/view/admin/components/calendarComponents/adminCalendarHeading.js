define([
	"jquery",
	"underscore",
	"view/base/components/calendarComponents/baseCalendarHeading"
], function ($, _, BaseCalendarHeading) {
	"use strict";

	var AdminCalendarHeading = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	}

	_.extend(AdminCalendarHeading.prototype, BaseCalendarHeading.prototype);
	_.extend(AdminCalendarHeading.prototype, {
		initialize: function () {

		}
	});

	return AdminCalendarHeading;


});