define([
	"jquery",
	"underscore",
	"view/student/components/calendarComponents/calendarHeading",
	"view/student/components/calendarComponents/calendarContent"
], function ($, _, CalendarHeading, CalendarContent) {
	"use strict";

	var Calendar = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Calendar.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: "body",
				headingSelector: "body",
				contentSelector: "body",
				$el: $(this.selector),
				content: new CalendarContent({
					selector: this.contentSelector,
					parent: this
				}),
				heading: new CalendarHeading({
					selector: this.headingSelector,
					parent: this
				})
			});
		},

		setView: function (viewToSet) {
			this.content.setView(viewToSet);
			this.heading.setView(viewToSet);
		}
	});

	return Calendar;
});