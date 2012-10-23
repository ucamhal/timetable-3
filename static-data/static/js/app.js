define([
	"jquery",
	"underscore",
	"view/student/components/inputArea",
	"view/student/components/results",
	"view/student/components/calendar",
	"control/hashController",
	"bootstrap"
], function ($, _, InputArea, Results, Calendar, HashController) {
	"use strict";

	var Application = function () {
		this.initialize();
	};

	_.extend(Application.prototype, {
		initialize: function () {

			_.mixin({
				capitalize: function (string) {
					return string.charAt(0).toUpperCase() + string.substring(1).toLowerCase();
				}
			});

			var inputArea = new InputArea({
					selector: "div#inputArea"
				}),
				results = new Results({
					selector: "div#results"
				}),
				calendar = new Calendar({
					selector: "div#calendarHolder",
					headingSelector: "div#calendarHeading",
					contentSelector: "div#calendar"
				}),
				hashController = new HashController({
					resultsView: results,
					calendarView: calendar,
					inputAreaView: inputArea
				});


			results.addEventListener("timetableChanged", function (event) {
				calendar.content.refresh();
			});

			$("a[href=\"#\"]").click(function (event) {
				event.preventDefault();
			});

			$(window).resize(function (e) {
				var maxWidth = $(window).width() - 200;

				if(maxWidth < 960) {
					maxWidth = 960;
				} else if (maxWidth > 1400) {
					maxWidth = 1400;
				}

				$("#inputArea > div").width(maxWidth);
				$("#uniLogo").width(maxWidth);
				$("#content").width(maxWidth);
				$("#actionsContainer").width(maxWidth);

				results.resize();
				calendar.resize({
					height: results.$el.height(),
					width: maxWidth - results.$el.outerWidth() - 50
				});

			});
			$(window).trigger("resize").trigger("hashchange");
		}
	});

	return Application;
});
