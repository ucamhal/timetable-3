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

			$("div.events table td > .icon-pencil").css("visibility", "hidden");
			$("div.events table td:not(.lectureActions)").hover(function () {
				$(this).find(".icon-pencil").css("visibility", "visible");
			}, function () {
				$(this).find(".icon-pencil").css("visibility", "hidden");
			});

			$(".seriesHeading h5 a").toggle(function (event) {
				$(this).parents(".module").find(".moduleHeading").addClass("hasOpenSeries");
				$(this).parents(".seriesHeading").removeClass("collapsed");
				$(this).parents(".series").find(".events").slideDown();
				$(this).parent().find("span").removeClass("icon-chevron-right").addClass("icon-chevron-down");
			}, function (event) {
				$(this).parents(".seriesHeading").addClass("collapsed");
				$(this).parents(".series").find(".events").slideUp();
				$(this).parent().find("span").removeClass("icon-chevron-down").addClass("icon-chevron-right");
				if ($(this).parents(".seriesList").find(".collapsed").length === $(this).parents(".seriesList").find(".seriesHeading").length) {
					$(this).parents(".module").find(".moduleHeading").removeClass("hasOpenSeries")
				}
			});

			$("div.events table td ul.buttons .icon-pencil").hover(function () {
				$(this).parent().parent().parent().parent().find("td > .icon-pencil").css("visibility", "visible");
			}, function () {
				$(this).parent().parent().parent().parent().find("td > .icon-pencil").css("visibility", "hidden");
			});
		}

	});

	return AdminApplication;
});
