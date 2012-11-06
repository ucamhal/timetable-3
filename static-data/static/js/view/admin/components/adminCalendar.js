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

			this.content.$el.hide();
			this.heading.$el.hide();

			$("#timetablesOverview li a", this.$el).click(function (event) {
				$.bbq.pushState({
					selectedTimetable: $(this).text()
				});

				return false;
			});

			$("#timetablesOverview li", this.$el).click(function (event) {
				$(this).find("a").trigger("click");
				event.preventDefault();
			});

			if (typeof $.bbq.getState("selectedTimetable") === "undefined") {
				$.bbq.pushState({
					selectedTimetable: ""
				});
			}
		},

		setTimetable: function (timetable) {
			if (typeof timetable !== "undefined" && timetable !== "" && timetable.toLowerCase() !== "new timetable") {
				$("#timetablesOverview", this.$el).hide();
				this.content.$el.show();
				this.content.refresh();
				$(window).trigger("resize");
				this.heading.$el.show();
			} else {
				$("#timetablesOverview", this.$el).show();
				this.content.$el.hide();
				this.heading.$el.hide();
				$(window).trigger("resize");
			}
		}
	});

	return AdminCalendar;
});