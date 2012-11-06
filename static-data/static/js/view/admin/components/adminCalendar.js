define([
	"jquery",
	"underscore",
	"view/base/components/baseCalendar",
	"view/admin/components/calendarComponents/adminCalendarContent",
	"view/admin/components/calendarComponents/adminCalendarHeading"
], function ($, _, BaseCalendar, AdminCalendarContent, AdminCalendarHeading) {

	var AdminCalendar = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(AdminCalendar.prototype, BaseCalendar.prototype);
	_.extend(AdminCalendar.prototype, {
		initialize: function () {
			_.defaults(this, {
				content: new AdminCalendarContent({
					selector: this.contentSelector,
					parent: this
				}),
				heading: new AdminCalendarHeading({
					selector: this.headingSelector,
					parent: this
				})
			});
		}
	});

	return AdminCalendar;
});