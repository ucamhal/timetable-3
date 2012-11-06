define([
	"jquery",
	"underscore"
], function ($, _) {
	"use strict";

	var BaseCalendar = function () {

	};

	_.extend(BaseCalendar.prototype, {
		baseInitialize: function () {
			_.defaults(this, {
				selector: "body",
				headingSelector: "body",
				contentSelector: "body",
				$el: $(this.selector),
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

	return BaseCalendar;

});