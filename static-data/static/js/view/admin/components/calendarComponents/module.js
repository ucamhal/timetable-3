define([
	"jquery",
	"underscore",
	"view/admin/components/calendarComponents/eventSeries"
], function ($, _, EventSeries) {
	"use strict";

	var Module = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Module.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: "body",
				$el: $(this.selector),
				series: [],
				collapsed: false
			});

			_.bindAll(this, "seriesToggleHandler");

			$(".series", this.$el).each(function () {
				self.series.push(new EventSeries({
					$el: $(this)
				}));
			});

			this.$el.on("seriesToggle", ".series", this.seriesToggleHandler);
			this.$el.on("click", ".moduleHeading h4 a", function (event) {
				self.collapsed = !self.collapsed;

				if (self.collapsed === true) {
					$(".moduleHeading span.icon-chevron-down", self.$el).toggleClass("icon-chevron-down", false).toggleClass("icon-chevron-right", true);
					$(".moduleContent", self.$el).slideUp();				
				} else {
					$(".moduleHeading span.icon-chevron-right", self.$el).toggleClass("icon-chevron-down", true).toggleClass("icon-chevron-right", false);
					$(".moduleContent", self.$el).slideDown();
				}
			});
		},

		hasOpenChanges: function () {
			return _.any(this.series, function (item) {
				return item.openChangesState;
			});
		},

		hasOpenSeries: function () {
			return _.any(this.series, function (item) {
				return item.collapsed === false;
			});
		},

		seriesToggleHandler: function () {
			this.showHideButtons(this.hasOpenSeries());
		},

		showHideButtons: function (visible) {
			$(".moduleHeading", this.$el).toggleClass("hasOpenSeries", visible);
		}
	});

	return Module;

});