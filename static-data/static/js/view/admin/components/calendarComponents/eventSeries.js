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
				editEnabled: false,
				openChangesState: false
			});

			_.bindAll(this, "editStateChangedHandler");
			_.bindAll(this, "dataChangedHandler");

			$(".event", this.$el).each(function () {
				var singleEvent = new Event({
					$el: $(this)
				});
				
				_.addEventListener(singleEvent.$el, "editStateChanged", self.editStateChangedHandler);
				_.addEventListener(singleEvent.$el, "dataChanged", self.dataChangedHandler);

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

		dataChangedHandler: function () {
			if (this.openChangesState === false) {
				this.openChangesState = true;
				$(".seriesEditActions", this.$el).slideDown();
			}			
		},

		editStateChangedHandler: function () {
			var newEditEnabled = this.checkEditEnabled();
			console.log("editStateChangedHandler eventSeries");

			if (this.editEnabled !== newEditEnabled) {
				console.log("inside if");
				this.editEnabled = newEditEnabled;

				if (this.editEnabled === false) {
					$(".seriesEditActions", this.$el).slideUp();
					this.openChangesState = false;
				}
			}

		},

		checkEditEnabled: function () {
			return _.any(this.events, function (item) {
				return item.editEnabled === true;
			});
		},

		cancelAllEdits: function () {
			this.openChangesState = false;
			_.each(this.events, function (item) {
				item.cancelEdit();
			});
		},

		saveAllEdits: function () {
			this.openChangesState = false;
			_.each(this.events, function (item) {
				item.saveEdits();
			});

			$(".changesNotificationPopup").modal();
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