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
	"bootstrapDatePicker",
	"bootstrapSpinner"
], function ($, _, BaseApplication, page, AdminInputArea, AdminCalendar, AdminResults) {
	"use strict";

	var AdminApplication = function () {
		var currentTime = new Date();
		this.baseInitialize();
		this.initialize();
		console.log("Application build time: " + (new Date() - currentTime) + "ms");
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

			_.defaults(this, {
				calendar: new AdminCalendar({
					selector: "#adminContent"
				})
			});

			/*

			var makeCellsEditable = function makeCellsEditable ($tr) {
				$tr.find("td").each(function (index, item) {

					if ($(this).hasClass("eventActions") === false) {
						var text = $(this).text();
						$(this).text("");

						$(this).append('<input type="text" />');
						$(this).find("input").val(text);
					}

				});
			};

			$("div.events table td:not(.eventActions)").click(function (event) {
				$(this).parent().addClass("editEnabled").find("td").unbind("hover").find(".icon-pencil").css("visibility", "visible");
				$(this).parent().find(".eventActions a").unbind("hover");
			});

			$("div.events table td.eventActions a").click(function (event) {
				switch ($(this).find("span").text()) {
				case "edit":
					$(this).unbind("hover").parent().parent().parent().parent().addClass("editEnabled").find("td").unbind("hover").find(".icon-pencil").css("visibility", "visible");
					makeCellsEditable($(this).parent().parent().parent().parent());
					break;
				case "duplicate":
					break;
				case "remove":
					break;
				}
				event.preventDefault();
			});

			

			$("div.events table td ul.buttons .icon-pencil").hover(function () {
				$(this).parent().parent().parent().parent().find("td > .icon-pencil").css("visibility", "visible");
			}, function () {
				$(this).parent().parent().parent().parent().find("td > .icon-pencil").css("visibility", "hidden");
			});*/
		}

	});

	return AdminApplication;
});
