define([
	"jquery",
	"underscore",
	"view/admin/components/calendarComponents/event"
], function ($, _, Event) {
	"use strict";

	var EventSeries = function (opt) {

		var self = this;
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(EventSeries.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				hashController: {},
				events: [],
				collapsed: true
			});

			$(".event", this.$el).each(function () {
				self.events.push(new Event({
					$el: $(this)
				}));
			});

			$(".seriesHeading h5 a", this.$el).click(function (event) {
				self.collapsed = !self.collapsed;
				_.dispatchEvent(self.$el, "seriesToggle");
				self.setCollapsedState(self.collapsed);
			});
		},

		setCollapsedState: function (collapsed, animationCallback) {
			$(".seriesHeading", this.$el).toggleClass("collapsed", collapsed);
			$(".seriesHeading h5 span", this.$el).toggleClass("icon-chevron-down", !collapsed).toggleClass("icon-chevron-right", collapsed);

			if (collapsed === false) {
				$(".events", this.$el).slideDown(animationCallback);
			} else {
				$(".events", this.$el).slideUp(animationCallback);
			}
		}
	});

	return EventSeries;

});