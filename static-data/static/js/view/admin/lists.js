define(["jquery", "underscore", "backbone"], function($, _, Backbone) {
	"use strict";

	/**
	 * Wraps a .js-module in the page to update the "> v" arrows when the
	 * module's content is shown/hidden. The actual showing/hiding is done by
	 * Bootstrap's collapse plugin.
	 */
	var ModuleView = Backbone.View.extend({
		constructor: function ModuleView() {
			ModuleView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"show .js-module-content": this.onExpand,
				"hide .js-module-content": this.onCollapse,
				"shown .js-module-content": this.onShown
			};
		},

		initialize: function() {
			_.bindAll(this, "onExpand", "onCollapse");
		},

		onExpand: function() {
			this.$(".js-expansion-indicator")
				.removeClass("icon-chevron-right")
				.addClass("icon-chevron-down");
		},

		onCollapse: function() {
			this.$(".js-expansion-indicator")
				.removeClass("icon-chevron-down")
				.addClass("icon-chevron-right");
			this.$(".js-module-content").removeClass("shown");
		},

		onShown: function() {
			this.$(".js-module-content").addClass("shown");
		}
	});
	
	var SeriesView = Backbone.View.extend({
		constructor: function SeriesView() {
			SeriesView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"show .js-events": this.onExpand,
				"shown .js-events": this.onShown,
				"hide .js-events": this.onCollapse,
			};
		},

		initialize: function() {
			_.bindAll(this);
		},

		isLoaded: function() {
			return this.$("table").length > 0;
		},

		isLoading: function() {
			return this.$(".js-loading-indicator").length > 0;
		},

		getSeriesId: function() {
			return this.$el.data("series-id");
		},

		/**
		 * Called when the series is first expanded in order to load events via
		 * AJAX.
		 */
		loadEvents: function() {
			// First we need to insert the loading indicator...
			
			// Find and copy the global loading indicator HTML
			var loadingEl = $(".js-loading-indicator-prototype").clone()
				.show()
				.removeClass("js-loading-indicator-prototype");
			this.loadingIndicator = new LoadingIndicatorView({el: loadingEl});
			this.$(".js-events").empty().append(this.loadingIndicator.el);
			this.loadingIndicator.on("retry", this.startEventsRequest, this);

			// Make the HTTP request to fetch the events
			this.startEventsRequest();
		},

		getEventsRequestOptions:  function() {
			return {};
		},

		startEventsRequest: function() {
			this.loadingIndicator.showLoadingState();

			// make the ajax request to fetch the events
			$.ajax("/series/" + encodeURIComponent(this.getSeriesId()) 
				+ "/list-events", this.getEventsRequestOptions())
				.done(this.onEventsFetched)
				.fail(this.onEventsFetchFailed);
		},

		onEventsFetched: function(response) {
			delete this.loadingIndicator;
			this.$(".js-loading-indicator").remove();
			this.$(".js-events").prepend(response);
		},

		onEventsFetchFailed: function() {
			this.loadingIndicator.showErrorState();
		},

		onExpand: function() {
			this.$(".js-expansion-indicator")
				.removeClass("icon-chevron-right")
				.addClass("icon-chevron-down");

			if(this.isLoaded() || this.isLoading()) {
				return;
			}

			this.loadEvents();
		},

		onCollapse: function() {
			this.$(".js-expansion-indicator")
				.removeClass("icon-chevron-down")
				.addClass("icon-chevron-right");
			this.$(".js-events").removeClass("shown");
		},

		onShown: function() {
			this.$(".js-events").addClass("shown");
		}
	});

	var WritableSeriesView = SeriesView.extend({
		constructor: function WritableSeriesView() {
			WritableSeriesView.__super__.constructor.apply(this, arguments);
		},

		getEventsRequestOptions: function() {
			var baseOptions = WritableSeriesView.__super__
				.getEventsRequestOptions();

			return _.extend(baseOptions, {
				data: {writeable: true}
			});
		},

		onEventsFetched: function() {
			// Call through to the superclass implementation in order to insert
			// the event elements into the page's DOM tree.
			WritableSeriesView.__super__.onEventsFetched.apply(this, arguments);

			// At this point the events exist in the page. Instanciate a 
			// WritableEventView wrapping each event and store the list of these
			// views in this.events
			this.events = _.map(this.$(".js-event"), function(eventEl) {
				return new WritableEventView({el: eventEl});
			});
		}
	});

	/**
	 * 
	 */
	var WritableEventView = Backbone.View.extend({
		constructor: function WritableEventView() {
			WritableEventView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				// The following 2 events enable firing of "change" events from
				// contenteditable elements on blur.
				"focusin [contenteditable]": this.onContenteditableFocus,
				"focusout [contenteditable]": this.onContenteditableBlur,

				"focusin .js-field": this.focusForEditing,
				"focusout .js-field": this.unfocusForEditing,

				// Watch for fields changing
				"change .js-field": this.updateModel,
				
				// Start editing when the pencil edit icon is clicked
				"click .js-edit-icon": this.startEditing,

				"click .js-date-time-cell": this.toggleDateTimeDialog,
				"click .js-date-time-dialog": this.onDateTimeDialogClicked
			};
		},

		initialize: function() {
			_.bindAll(this);

			// focus/blur events have to be bound manually, otherwise the
			// delegated focusin/focusout verisons are used.
			this.$(".js-date-time-cell .js-focus-catcher")
				.on("focus", this.toggleDateTimeDialog);

			this.$title = this.$(".js-field-title");
			this.$location = this.$(".js-field-location");
			this.$type = this.$(".js-field-type");
			this.$people = this.$(".js-field-people");
			this.$week = this.$(".js-field-week");
			this.$term = this.$(".js-field-term");
			this.$day = this.$(".js-field-day");
			this.$startHour = this.$(".js-field-start-hour");
			this.$startMinute = this.$(".js-field-start-minute");
			this.$endHour = this.$(".js-field-end-hour");
			this.$endMinute = this.$(".js-field-end-minute");

			this.model = new EventModel();
			// Push the state of the HTML into the model
			this.updateModel();
			// Tell the model that it's current state is the initial one
			this.model.storeInitialState();

			this.model.on("change", this.render);
		},

		render: function() {
			// We only need to update the date/time fields, the rest are kept
			// automatically as they're contenteditable=true
			this.$week.text(this.model.get("week"));
			this.$term.text(this.model.getPrettyTerm());
			this.$day.text(this.model.getPrettyDay());
			this.$startHour.text(this.model.get("startHour"));
			this.$startMinute.text(this.model.get("startMinute"));
			this.$endHour.text(this.model.get("endHour"));
			this.$endMinute.text(this.model.get("endMinute"));
		},

		updateModel: function() {
			// Update our model with the current state of the HTML
			this.model.set({
				title: this.$title.text(),
				location: this.$location.text(),
				type: this.$type.text(),
				people: this.$people.text(),
				week: this.$week.text(),
				term: this.$term.text(),
				day: this.$day.text(),
				startHour: this.$startHour.text(),
				startMinute: this.$startMinute.text(),
				endHour: this.$endHour.text(),
				endMinute: this.$endMinute.text()
			});
		},

		focusForEditing: function() {
			console.log("focusForEditing", arguments);
			this.$el.addClass("being-edited");
		},

		/** S */
		unfocusForEditing: function(event) {
			console.log("unfocusForEditing", "event:", event, "focused:", $(":focus"));
			this.$el.removeClass("being-edited");

			// Mark the event as changed if it's been modified
			this.markAsChanged(this.model.hasChangedFromOriginal());
		},

		markAsChanged: function(isChanged) {
			isChanged = Boolean(isChanged);
			this.isUnsaved = isChanged;
			this.trigger("event:savedStatusChanged")
			
			if(isChanged)
				this.$el.addClass("unsaved");
			else
				this.$el.removeClass("unsaved");
		},

		/** Starts editing this event by focusing the title element. */
		startEditing: function() {
			this.$title.focus();
		},

		onDateTimeDialogClicked: function(event) {
			// Prevent click events on the date/time dialog reaching the 
			// toggleDateTimeDialog() handler, which would close the dialog.
			event.stopPropagation();
		},

		closeDateTimeDialog: function() {
			if(this.dateTimeDialog) {
				this.dateTimeDialog.remove();
				delete this.dateTimeDialog;
			}
		},

		toggleDateTimeDialog: function(event) {

			var isFocus = event.type === "focus";
			var isBeforeDialog = $(event.currentTarget)
				.hasClass("js-focus-catcher-before");

			if(this.dateTimeDialog) {
				console.log("closing dialog", event);
				this.closeDateTimeDialog();

				// Move focus from this focus catcher to a real element if the
				// dialog close was triggered by focusing a focus catching
				// element before/after the dialog in the DOM.
				if(isFocus) {
					if(isBeforeDialog)
						this.$(".js-field-type").focus();
					else
						this.$(".js-field-location").focus();
				}
			}
			else {
				console.log("opening dialog", event);
				this.dateTimeDialog = new DateTimeDialogView({
					el: $(".js-date-time-dialog").clone(),
					model: this.model
				});
				// dialog:close is fired by the dialog when a click is made
				// outside its area, or the close icon is clicked.
				this.dateTimeDialog.on(
					"dialog:close", this.closeDateTimeDialog);

				this.$(".js-date-time-cell .js-dialog-holder")
					.append(this.dateTimeDialog.$el);
				this.dateTimeDialog.$el.show();

				if(!isFocus || isBeforeDialog)
					this.dateTimeDialog.focusStart();
				else
					this.dateTimeDialog.focusEnd();
			}
		},

		onContenteditableFocus: function(event) {
			// Stash the element's value in a data property before it's edited
			// so that we can fire a change event if it's modified.
			var $el = $(event.target);
			$el.data("__contenteditablePrevValue", $el.html());
		},

		onContenteditableBlur: function(event) {
			var $el = $(event.target);
			var html = $el.html();
			if($el.data("__contenteditablePrevValue") !== html) {
				// Delete the remembered HTML text
				$el.data("__contenteditablePrevValue", undefined);
				$el.trigger("change");
			}
		}
	});

	var EventModel = Backbone.Model.extend({
		constructor: function EventModel() {
			EventModel.__super__.constructor.apply(this, arguments);
		},

		initialize: function() {

			this.hasInitialState = false;
		},

		titleCase: function(str) {
			if(str.length > 0)
				return str[0].toUpperCase() + str.slice(1);
			return str;
		},

		getPrettyTerm: function() {
			var term = this.get("term");
			if(term)
				return this.titleCase(term);
			return term;
		},

		getPrettyDay: function() {
			var day = this.get("day");
			if(day)
				return this.titleCase(day);
			return day;
		},

		/**
		 * Mark the event's current state as being the original. After calling
		 * this, hasChangedFromOriginal() may be called.
		 */
		storeInitialState: function() {
			if(!this.hasInitialState === false) {
				throw new Error("Initial state already set.");
			}

			this.hasInitialState = true;
			this.originalAttributes = this.toJSON();
		},

		validate: function(attrs) {
			return;

			var errors = {};

			if(!attrs.title || attrs.title.trim() == "")
				errors.title = ["This field is required."];

			if(!attrs.type || attrs.type == "")
				errors.type = ["This field is required."];

			if(!attrs.location || attrs.location.trim() == "")
				errors.location = ["This field is required."];

			if(!attrs.people || attrs.people.trim() == "")
				errors.people = ["This field is required."];
		},

		/** 
		 * Returns true if the current attribute values differ from the initial
		 * values.
		 */
		hasChangedFromOriginal: function() {
			if(!this.hasInitialState === true) {
				throw new Error("No initial state set.");
			}
			return !_.isEqual(this.originalAttributes, this.toJSON());
		},
	});

	var DateTimeDialogView = Backbone.View.extend({
		constructor: function DateTimeDialogView() {
			DateTimeDialogView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"click .js-close-btn": this.requestDialogClose,
				"change input": this.onFieldUpdated,
				"change select": this.onFieldUpdated,
			};
		},

		initialize: function() {
			_.bindAll(this);

			this.backdrop = new DialogBackdropView();
			this.backdrop.$el.addClass("dialog-backdrop-date-time");
			$("body").append(this.backdrop.el);
			this.backdrop.on("clicked", this.requestDialogClose);

			this.$week = this.$("#date-time-week");
			this.$term = this.$("#date-time-term");
			this.$day = this.$("#date-time-day");
			this.$startHour = this.$("#date-time-start-hour");
			this.$startMinute = this.$("#date-time-start-minute");
			this.$endHour = this.$("#date-time-end-hour");
			this.$endMinute = this.$("#date-time-end-minute");

			// Initialise the inputs
			this.render();
		},

		/** Update the state of hte DOM with the model's state. */
		render: function() {
			this.$week.val(this.model.get("week"));
			this.$term.val(this.model.get("term"));
			this.$day.val(this.model.get("day"));
			this.$startHour.val(this.model.get("startHour"));
			this.$startMinute.val(this.model.get("startMinute"));
			this.$endHour.val(this.model.get("endHour"));
			this.$endMinute.val(this.model.get("endMinute"));
		},

		follow: function follow(start, finish, updated, isStart) {
			if(isStart) {
				if(updated > start)
					return [updated, finish + (updated - start)];
				return [updated, finish];
			}
			else {
				if(updated < finish)
					return [start + (updated - finish), updated];
				return [start, updated];
			}
		},

		onFieldUpdated: function(event) {
			var $target = $(event.target);

			// Has a time changed?
			if($target.parents(".date-time-form-row").length > 0) {

				var isStart = $target.hasClass("js-start");
				var isHour = $target.hasClass("js-hour");

				// Prevent invalid numbers creaping in
				var num = Number($target.val());
				if(isNaN(num)) {
					var attr = (isStart? "start" : "end")
						+ (isHour ? "Hour" : "Minute");
					num = this.model.get(attr);
					$target.val(num);
				}
				
				// FIXME: we should do this on total minutes rather than
				// individually...
				if(isHour) {
					var start = Number(this.model.get("startHour"));
					var end = Number(this.model.get("endHour"));
					var updated = Number($target.val());
					var hours = this.follow(start, end, updated, isStart);

					this.$startHour.val(Math.max(0, Math.min(24, hours[0])));
					this.$endHour.val(Math.max(0, Math.min(24, hours[1])));
				}
				else {
					var start = Number(this.model.get("startMinute"));
					var end = Number(this.model.get("endMinute"));
					var updated = Number($target.val());
					var minutes = this.follow(start, end, updated, isStart);

					this.$startMinute.val(Math.max(0, Math.min(59, minutes[0])));
					this.$endMinute.val(Math.max(0, Math.min(59, minutes[1])));
				}
			}
			this.syncToModel();
		},

		/** Update the state of the model with the DOM's state. */
		syncToModel: function() {
			this.model.set({
				week: this.$week.val(),
				term: this.$term.val(),
				day: this.$day.val(),
				startHour: this.$startHour.val(),
				startMinute: this.$startMinute.val(),
				endHour: this.$endHour.val(),
				endMinute: this.$endMinute.val()
			});
		},

		/** Focus the first form element. */
		focusStart: function() {
			this.$(".js-week").focus();
		},

		/** Focus the last form element. */
		focusEnd: function() {
			this.$(".js-end-minute").focus();
		},

		remove: function() {
			// Remove our backdrop element when we're removed.
			this.backdrop.remove();
			// Call the superclass's remove()
			DateTimeDialogView.__super__.remove.apply(this, arguments);
		},

		requestDialogClose: function() {
			this.trigger("dialog:close");
		}
	});

	var DialogBackdropView = Backbone.View.extend({
		constructor: function DialogBackdropView() {
			DialogBackdropView.__super__.constructor.apply(this, arguments);
		},

		tagName: "div",
		className: "dialog-backdrop",

		events: function() {
			return {
				"click": this.onClick
			};
		},

		onClick: function() {
			this.trigger("clicked");
		}
	});

	/**
	 * Controlls a .js-loading-indicator. Shows a progress bar when loading
	 * and an error message with a retry button when failed.
	 */
	var LoadingIndicatorView = Backbone.View.extend({
		constructor: function LoadingIndicatorView() {
			LoadingIndicatorView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"click .js-retry-btn": "onRetry"
			};
		},

		initialize: function() {
			_.bindAll(this, "onRetry");
		},

		onRetry: function() {
			this.trigger("retry");
		},

		showLoadingState: function() {
			$(".loading").show();
			$(".error").hide();
		},

		showErrorState: function() {
			$(".loading").hide();
			$(".error").show();
		}
	});

	function bindContentEditableChangeTrigger(targetEl) {
		_.each($("[contenteditable!=false]", targetEl), function(editableEl) {

		});
	}

	return {
		ModuleView: ModuleView,
		SeriesView: SeriesView,
		WritableSeriesView: WritableSeriesView
	};
});