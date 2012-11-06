define([
	"jquery",
	"underscore",
	"view/base/components/baseResults"
], function ($, _, BaseResults) {
	"use strict";

	var AdminResults = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	}

	_.extend(AdminResults.prototype, BaseResults.prototype);
	_.extend(AdminResults.prototype, {

		initialize: function () {

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector)
			});

		 	$("#resultsHead form#addModule .timepicker-default").timepicker();

			$("#resultsHead a.addModule", this.$el).toggle(function (event) {
				$("#resultsHead form#addModule", this.$el).slideDown(200);
				event.preventDefault();
			}, function (event) {
				$("#resultsHead form#addModule", this.$el).slideUp(200);
				event.preventDefault();
			});

			$("#resultsHead form#addModule a").click(function (event) {
				switch ($(this).text().toLowerCase()) {
					case "cancel":
						$("#resultsHead a.addModule", self.$el).trigger("click");
						break;
					case "add module":
						break;
				}

				event.preventDefault();
			});

		},

		setTimetable: function (timetable) {
			if (typeof timetable !== "undefined" && timetable !== "" && timetable.toLowerCase() !== "new timetable") {
				$("> *", this.$el).show();
			} else {
				$("> *", this.$el).hide();
			}
		}

	});

	return AdminResults;
});