define([
	"jquery",
	"underscore",
	"view/base/components/calendarComponents/baseCalendarContent",
	"view/admin/components/calendarComponents/adminCalendarPopup"
], function ($, _, BaseCalendarContent, AdminCalendarPopup) {

	"use strict";

	var AdminCalendarContent = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(AdminCalendarContent.prototype, BaseCalendarContent.prototype);
	_.extend(AdminCalendarContent.prototype, {
		initialize: function () {
			_.defaults(this, {
				//CalendarPopup: AdminCalendarPopup
			});
		}
	});

	return AdminCalendarContent;

});