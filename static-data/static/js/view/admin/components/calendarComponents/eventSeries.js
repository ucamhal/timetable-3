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
				$serverErrorPopup: $(".formServerErrorPopup"),
				$validationErrorPopup: $(".formValidationErrorPopup"),
				eventsInitialized: false,
				savingState: false
			});

			_.bindAll(this, "editStateChangedHandler");
			_.bindAll(this, "dataChangedHandler");
			_.bindAll(this, "eventFocusHandler");
			_.bindAll(this, "activeEventChangedHandler");

			this.$el.on("editStateChanged", ".event", self.editStateChangedHandler);
			this.$el.on("dataChanged", ".event", self.dataChangedHandler);
			this.$el.on("hasFocus", ".event", self.eventFocusHandler);
			this.$el.on("activeStateEnabled", ".event", self.activeEventChangedHandler);

			this.$el.on("click", ".seriesHeading h5 a", function (event) {
				self.collapsed = !self.collapsed;
				_.dispatchEvent(self.$el, "seriesToggle");
				self.setCollapsedState(self.collapsed);
			});

			this.$el.on("click", ".seriesEditActions .save", function (event) {
				if (self.savingState === false) {
					self.saveAllEdits();
					event.preventDefault();
				}
			}).button();

			this.$el.on("click", ".seriesEditActions .cancel", function (event) {
				if (self.savingState === false) {
					self.cancelAllEdits();
					event.preventDefault();
				}
			});
		},

		activeEventChangedHandler: function (event, singleEvent) {
			this.unsetEventsActiveState([singleEvent]);
		},

		unsetEventsActiveState: function (exclude) {
			var exclude = typeof exclude === "undefined" ? [] : exclude;
			_.each(_.difference(this.events, exclude), function (item) {
				item.toggleActiveState(false);
			});
		},

		eventFocusHandler: function (event, singleEvent) {
			this.unsetEditEnabledStateForUnchangedEvents([singleEvent]);
		},

		unsetEditEnabledStateForUnchangedEvents: function (exclude) {
			var exclude = typeof exclude === "undefined" ? [] : exclude;
			_.each(_.difference(this.events, exclude), function (item) {
				if (item.editEnabled === true && item.dataChanged() === false) {
					item.toggleEditEnabledState();
				}
			});
		},

		setSavingState: function (state) {
			this.savingState = state;
			$(".seriesEditActions .save", this.$el).button((function () {
				if (state === true) {
					return "loading";
				}
				return "reset";
			}()));
			$(".seriesEditActions .cancel", this.$el).toggleClass("mute", state);
			_.each(this.events, function (item) {
				item.setDisabled(state);
			});
		},

		buildEvents: function (checkForErrorsOnInit) {
			var self = this,
				checkForErrorsOnInit = typeof checkForErrorsOnInit === "undefined" ? false : checkForErrorsOnInit;

			$(".event", this.$el).each(function () {
				self.events.push(new Event({
					$el: $(this),
					checkForErrorsOnInit: checkForErrorsOnInit
				}));
			});
		},

		dataChangedHandler: function () {
			this.toggleOpenChangesState(true);
		},

		editStateChangedHandler: function () {
			var newEditEnabled = this.checkEditEnabled();
			if (this.editEnabled !== newEditEnabled) {
				this.editEnabled = newEditEnabled;

				if (this.editEnabled === false) {
					this.toggleOpenChangesState(false);
				}
			}
		},

		toggleOpenChangesState: function (openChanges) {
			this.openChangesState = typeof openChanges === "undefined" ? !this.openChangesState : openChanges;
			if (this.openChangesState === true) {
				$(".seriesEditActions", this.$el).slideDown();
			} else {
				$(".seriesEditActions", this.$el).slideUp();
			}
		},

		checkEditEnabled: function () {
			return _.any(this.events, function (item) {
				return item.editEnabled === true;
			});
		},

		cancelAllEdits: function () {
			this.toggleOpenChangesState(false);
			_.each(this.events, function (item) {
				item.cancelEdit();
			});
		},

		saveAllEdits: function () {
			var self = this,
				data = $("> form", this.$el).serialize();

			this.toggleOpenChangesState(false);
			this.setSavingState(true);
			
			$.ajax({
				type: "POST",
				url: $("> form", this.$el).attr("action"),
				data: data,
				success: function (data) {
					self.setSavingState(false);
					$(".events", self.$el).empty().append($(".events", $(data)).html());
					self.events = [];
					self.buildEvents(true);
					//TODO check form rather than .event
					if ($(".events .error").length > 0) {
						self.handleValidationErrors();
					} else {
						self.handleNotifications();
					}
				},
				error: function () {
					self.setSavingState(false);
					self.handleServerErrors();
				}
			});
		},

		handleValidationErrors: function () {
			this.$validationErrorPopup.modal();
		},

		handleServerErrors: function () {
			this.$serverErrorPopup.modal();
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