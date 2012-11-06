define(["jquery", "underscore", "jquery-bbq"], function ($, _) {
	"use strict";

	var HashController = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(HashController.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				parameters: {
					calendarView: function (val) {
						var viewToSet = "agendaWeek";

						switch (val) {
						case "week":
							viewToSet = "agendaWeek";
							break;
						case "month":
							viewToSet = "month";
							break;
						case "list":
							viewToSet = "list";
							break;
						}
						this.calendarView.setView(viewToSet);
					},

					path: function (thingPath) {
						this.inputAreaView.updateSelectBoxes(thingPath);
						this.resultsView.updateResults(thingPath);
					},

					selectedTimetable: function (selectedTimetable) {
						this.calendarView.setTimetable(selectedTimetable);
						this.resultsView.setTimetable(selectedTimetable);
					}
				},

				previousState: {}
			});

			$(window).bind("hashchange", function () {
				var i,
					parametersLength = self.parameters.length,
					currentState = $.bbq.getState(),
					key;

				for (key in currentState) {
					if (currentState.hasOwnProperty(key)) {
						if (typeof self.parameters[key] !== "undefined" && (typeof self.previousState[key] === "undefined" || self.previousState[key] !== currentState[key])) {
							self.parameters[key].call(self, currentState[key]);
						}
					}
				}

				self.previousState = currentState;
			});
		}
	});

	return HashController;
});