define(['jquery', 'underscore', 'jquery-bbq'], function ($, _) {
	"use strict";

	var HashController = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(HashController.prototype, {
		initialize: function () {
			var self = this;
			// FIXME: modify this code to store the state correctly, only the part parameter is needed, and that should not be called part (as its not a part)
			// FIXME: "path" might be a better term since thats what it is.
			_.defaults(this, {
				parameters: [
					{
						name: 'calendarView',
						action: function (val) {
							var viewToSet = 'agendaWeek';

							switch (val) {
							case 'week':
								viewToSet = 'agendaWeek';
								break;
							case 'month':
								viewToSet = 'month';
								break;
							}
							this.calendarView.content.setView(viewToSet);
						}
					},
					{
						name: 'course',
						action: function (val) {
							this.inputAreaView.updateSelectedCourse(val);
							this.inputAreaView.updatePartOptions(val);
							this.resultsView.updateResults($.bbq.getState('part'));
						}
					},
					{
						name: 'part',
						action: function (val) {
							this.inputAreaView.updateSelectedPart(val);
							this.resultsView.updateResults($.bbq.getState('part'));
						}
					}
				],
				previousState: {}
			});

			$(window).bind('hashchange', function () {
				var i,
					parametersLength = self.parameters.length,
					currentState = $.bbq.getState(),
					key;

				for (key in currentState) {
					if(typeof self.previousState[key] === 'undefined' || self.previousState[key] !== currentState[key]) {
						for (i = 0; i < parametersLength; i += 1) {
							if (self.parameters[i].name === key) {
								self.parameters[i].action.call(self, currentState[key]);
							}
						}
					}
				}
				/*
				for (i = 0; i < parametersLength; i += 1) {
					if ($.bbq.getState(self.parameters[i].name)) {
						self.parameters[i].action.call(self, $.bbq.getState(self.parameters[i].name));
					}
				}*/

				self.previousState = currentState;
			});
		}
	});

	return HashController;
});