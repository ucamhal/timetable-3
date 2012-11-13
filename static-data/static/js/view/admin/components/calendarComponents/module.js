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
				series: []
			});

			_.bindAll(this, "seriesToggleHandler");

			$(".series", this.$el).each(function () {

				var series = new EventSeries({
					$el: $(this)
				});

				_.addEventListener(series.$el, "seriesToggle", self.seriesToggleHandler);

				self.series.push(series);
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