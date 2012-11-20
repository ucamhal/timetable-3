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
				self.series.push(new EventSeries({
					$el: $(this)
				}));
			});

			this.$el.on("seriesToggle", ".series", this.seriesToggleHandler);
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