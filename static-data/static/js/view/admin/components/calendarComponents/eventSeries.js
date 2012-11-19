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
				openChangesState: false,
				$notificationsPopup: $(".changesNotificationPopup"),
				eventsInitialized: false
			});

			_.bindAll(this, "editStateChangedHandler");
			_.bindAll(this, "dataChangedHandler");

			this.$el.on("editStateChanged", ".event", self.editStateChangedHandler);
			this.$el.on("dataChanged", ".event", self.dataChangedHandler);

			this.$el.on("click", ".seriesHeading h5 a", function (event) {
				self.collapsed = !self.collapsed;
				_.dispatchEvent(self.$el, "seriesToggle");
				self.setCollapsedState(self.collapsed);
			});

			this.$el.on("click", ".seriesEditActions .save", function (event) {
				self.saveAllEdits();
				event.preventDefault();
			});

			this.$el.on("click", ".seriesEditActions .cancel", function (event) {
				self.cancelAllEdits();
				event.preventDefault();
			});
		},

		buildEvents: function () {
			var self = this;

			$(".event", this.$el).each(function () {
				self.events.push(new Event({
					$el: $(this)
				}));
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
			if (this.editEnabled !== newEditEnabled) {
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
			var self = this;
			this.openChangesState = false;
			
			$.post($("> form", this.$el).attr("action"), $("> form", this.$el).serialize(), function (data) {
				$(".events", self.$el).empty().append($(".events", $(data)).html());
				self.events = [];
				self.buildEvents();
			});
			
			this.handleNotifications();
		},

		handleNotifications: function () {
			var self = this;

			this.$notificationsPopup.modal().find("a").click(function (event) {
				
				if ($(this).hasClass("dontSendNotification")) {
					self.$notificationsPopup.modal("hide");
				} else if ($(this).hasClass("sendNotifcation")) {
					self.$notificationsPopup.modal("hide");
					self.sendNotifications();
				}

				event.preventDefault();
			});
		},

		sendNotifications: function () {

		},

		setCollapsedState: function (collapsed, animationCallback) {
			$(".seriesHeading", this.$el).toggleClass("collapsed", collapsed);
			$(".seriesHeading h5 span", this.$el).toggleClass("icon-chevron-down", !collapsed).toggleClass("icon-chevron-right", collapsed);

			if (collapsed === false) {
				if (this.eventsInitialized === false) {
					var currentTime = new Date();
					this.eventsInitialized = true;
					this.buildEvents();
					console.log("Single EventSeries build time: " + (new Date() - currentTime) + "ms");
				}
				$(".events", this.$el).slideDown(animationCallback);
			} else {
				$(".events", this.$el).slideUp(animationCallback);
			}
		}
	});

	return EventSeries;

});