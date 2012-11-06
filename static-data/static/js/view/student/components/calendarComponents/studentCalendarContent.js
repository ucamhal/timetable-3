define([
	"jquery",
	"underscore",
	"view/base/components/calendarComponents/baseCalendarContent",
	"view/student/components/calendarComponents/listView",
	"view/student/components/calendarComponents/studentCalendarPopup",
	"fullcalendar"
], function ($, _, BaseCalendarContent, ListView, StudentCalendarPopup) {
	"use strict";
	var StudentCalendarContent = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(StudentCalendarContent.prototype, BaseCalendarContent.prototype);
	_.extend(StudentCalendarContent.prototype, {
		initialize: function () {
			_.defaults(this, {
				CalendarPopup: StudentCalendarPopup,
				listView: new ListView({
					selector: "#listView",
					parent: this
				})
			});
		},

		showNext: function () {
			this.clearCalendarPopups();
			this.$el.fullCalendar("next");
			if (this.activeView === "list") {
				this.renderListView();
			}
		},

		showPrev: function () {
			this.clearCalendarPopups();
			this.$el.fullCalendar("prev");
			if (this.activeView === "list") {
				this.renderListView();
			}
		},

		renderListView: function () {
			this.listView.render({
				year: _.getYearFromDate(this.getActiveDate()),
				month: _.getMonthFromDate(this.getActiveDate())
			});
		},

		setView: function (view) {
			this.clearCalendarPopups();
			this.activeView = view;

			if (view === "list") {
				$(".fc-content", this.$el).hide();
				this.$el.fullCalendar("changeView", "month");
				this.renderListView();
				this.listView.$el.show();
			} else {
				$(".fc-content", this.$el).show();
				this.listView.$el.hide();
				this.$el.fullCalendar("changeView", view);
			}
		}
	});

	return StudentCalendarContent;
});