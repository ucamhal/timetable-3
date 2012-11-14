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
				collapsed: true,
				editEnabled: false
			});

			_.bindAll(this, "editStateChangedHandler");

			$(".event", this.$el).each(function () {
				var singleEvent = new Event({
					$el: $(this)
				});
				
				_.addEventListener(singleEvent.$el, "editStateChanged", self.editStateChangedHandler);

				self.events.push(singleEvent);
			});

			$(".seriesHeading h5 a", this.$el).click(function (event) {
				self.collapsed = !self.collapsed;
				_.dispatchEvent(self.$el, "seriesToggle");
				self.setCollapsedState(self.collapsed);
			});

			$(".seriesEditActions .save", this.$el).click(function (event) {
				self.saveAllEdits();
				event.preventDefault();
			});

			$(".seriesEditActions .cancel", this.$el).click(function (event) {
				self.cancelAllEdits();
				event.preventDefault();
			});
		},

		editStateChangedHandler: function () {
			var newEditEnabled = this.checkEditEnabled();

			if (this.editEnabled !== newEditEnabled) {
				this.editEnabled = newEditEnabled;

				if (this.editEnabled === true) {
					$(".seriesEditActions", this.$el).slideDown();
				} else {
					$(".seriesEditActions", this.$el).slideUp();
				}
			}

		},

		checkEditEnabled: function () {
			return _.any(this.events, function (item) {
				return item.editEnabled === true;
			});
		},

		cancelAllEdits: function () {
			_.each(this.events, function (item) {
				item.cancelEdit();
			});
		},

		saveAllEdits: function () {
			_.each(this.events, function (item) {
				item.saveEdits();
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