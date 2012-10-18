define([
	'jquery',
	'underscore',
	'view/student/components/inputArea',
	'view/student/components/results',
	'view/student/components/calendar',
	'control/hashController'
], function ($, _, InputArea, Results, Calendar, HashController) {
	"use strict";

	var Application = function () {
		this.initialize();
	};

	_.extend(Application.prototype, {
		initialize: function () {

			var inputArea = new InputArea({
				selector: 'div#inputArea'
			}),
				results = new Results({
				selector: 'div#results'
			}),
				calendar = new Calendar({
				selector: 'div#calendarHolder',
				headingSelector: 'div#calendarHeading',
				contentSelector: 'div#calendar'
			}),
				hashController = new HashController({
				resultsView: results,
				calendarView: calendar
			});


			$('a[href="#"]').click(function (event) {
				event.preventDefault();
			});

			$(window).trigger('hashchange');
		}
	});

	return Application;
});
