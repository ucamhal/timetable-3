define([
	'jquery',
	'underscore',
	'view/student/components/calendarComponents/calendarHeading',
	'view/student/components/calendarComponents/calendarContent'
], function ($, _, CalendarHeading, CalendarContent) {
	"use strict";

	var Calendar = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Calendar.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: 'body',
				headingSelector: 'body',
				contentSelector: 'body',
				$el: $(this.selector),
				heading: new CalendarHeading({
					selector: this.headingSelector,
					parent: this
				}),
				content: new CalendarContent({
					selector: this.contentSelector,
					parent: this
				})
			});
		}
	});

	return Calendar;
});