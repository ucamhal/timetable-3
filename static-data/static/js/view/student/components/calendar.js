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
				}),
				size: {
					width: 0,
					height: 0
				}
			});
		},

		setView: function (viewToSet) {
			this.content.setView(viewToSet);
			this.heading.setView(viewToSet);
			this.resize();
		},

		resize: function (to) {
			to = to || this.size;

			this.$el.height(to.height);
			this.$el.width(to.width);

			this.content.setHeight(this.$el.height() - this.heading.$el.outerHeight());
			this.size = to;
		}
	});

	return Calendar;
});