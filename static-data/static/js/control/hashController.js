define(['jquery', 'underscore', 'jquery-bbq'], function ($, _) {
	"use strict";

	var HashController = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(HashController.prototype, {
		initialize: function () {
			var self = this;

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
					}
				]
			});

			$(window).bind('hashchange', function () {
				var i,
					parametersLength = self.parameters.length;

				for (i = 0; i < parametersLength; i += 1) {
					if ($.bbq.getState(self.parameters[i].name)) {
						self.parameters[i].action.call(self, $.bbq.getState(self.parameters[i].name));
					}
				}
			});
		}
	});

	return HashController;
});