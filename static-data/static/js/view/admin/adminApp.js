define([
	"jquery",
	"underscore",
	"view/base/baseApp",
	"util/page",
	"view/admin/components/adminInputArea",
	"view/admin/components/adminCalendar",
	"view/admin/components/adminResults",
	"bootstrap",
	"bootstrapTimePicker",
	"bootstrapDatePicker"
], function ($, _, BaseApplication, page, AdminInputArea, AdminCalendar, AdminResults) {
	"use strict";

	var AdminApplication = function () {
		this.initialize();
		//this.baseInitialize();
	}

	_.extend(AdminApplication.prototype, BaseApplication.prototype)
	_.extend(AdminApplication.prototype, {

		initialize: function () {
			/*
			_.defaults(this, {
				results: new AdminResults({
					selector: "div#results"
				}),
				calendar: new AdminCalendar({
					selector: "div#calendarHolder",
					headingSelector: "div#calendarHeading",
					contentSelector: "div#calendar"
				}),
				inputArea: new AdminInputArea({
					selector: "div#inputArea"
				})
			});*/

			$(".accordion-body").on("show", function () {
				$(this).prev().find("span.icon-folder-close").removeClass("icon-folder-close").addClass("icon-folder-open");
			});

			$(".accordion-body").on("hide", function () {
				$(this).prev().find("span.icon-folder-open").removeClass("icon-folder-open").addClass("icon-folder-close");
			});
		}

	});

	return AdminApplication;
});
