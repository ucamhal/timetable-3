define(["jquery", "underscore", "backbone", "util/django-forms",
			"util/assert", "jquery-bbq", "bootstrapTypeahead"],
		function($, _, Backbone, DjangoForms, assert) {
	"use strict";

	var listEvents = _.extend({}, Backbone.Events);

	/** Strip leading zeros from an integer such as: 01, 05, 005 etc. */
	function stripZeros(str) {
		var groups = /(-*)0*(\d+)/.exec(str);
		if(!groups)
			return undefined;

		var integer = groups[2];
		if( groups[1] == '-' ) { // handle negative values
			integer = -integer
		}
		return integer;
	}

	/** As parseInt() except handles strings with leading zeros correctly. */
	function safeParseInt(str) {
		return parseInt(stripZeros(str));
	}
	
	var BaseModel = Backbone.Model.extend({
		initialize: function () {
			this.hasInitialState = false;
			this.on("change", this.onChange);
		},
		
		onChange: function () {
			listEvents.trigger("page-edited");
		},

		/** 
		 * Resets the model's attributes to the initial values.
		 */
		reset: function () {
			this.set(this.originalAttributes);
		},

		/**
		 * Mark the event's current state as being the original. After calling
		 * this, hasChangedFromOriginal() may be called.
		 */
		storeInitialState: function (force) {
			if (this.hasInitialState === true && force !== true) {
				throw new Error("Initial state already set.");
			}

			this.hasInitialState = true;
			this.originalAttributes = this.toJSON();
		},

		/** 
		 * Returns true if the current attribute values differ from the initial
		 * values.
		 */
		hasChangedFromOriginal: function () {
			if (this.hasInitialState === false) {
				throw new Error("No initial state set.");;
			}

			return !_.isEqual(this.originalAttributes, this.toJSON());
		},

		hasFieldChangedFromOriginal: function (fieldName) {
			return !_.isEqual(this.get(fieldName), this.originalAttributes[fieldName]);
		}
	});
	
	
	var Locker = Backbone.View.extend({
		initialize: function (opts) {
			_.bindAll(this, "ping");
			_.bindAll(this, "preventTimeout");
			
			this.preventTimeoutTime = opts.preventTimeoutTime || 5000;
			this.pingTime = opts.pingTime || 5000;
			this.$timedOutModal = opts.$timedOutModal;
			this.refreshUrl = opts.refreshUrl || "";
			
			this.onTimeoutCallback = opts.onTimeout;
			this.setTimedOutState(false);
			
			this.pingInterval = setInterval(this.ping, this.pingTime);
			this.preventTimeout = _.throttle(this.preventTimeout, this.preventTimeoutTime);
			
			this.ping();
		},

		postponePing: function () {
			clearInterval(this.pingInterval);
			this.pingInterval = setInterval(this.ping, this.pingTime);
		},
		
		/**
		 * Function that returns true if the lock has timed out
		 * @return {boolean} Returns true if the lock has timed out
		 */
		isTimedOut: function () {
			return this.timedOut;
		},
		
		/**
		 * Function that sets the timeout state of the lock and triggers a popup if true.
		 * @param {boolean} timedOut The timed out state. Inverts current state by default.
		 */
		setTimedOutState: function (timedOut) {
			typeof timedOut !== "undefined" ? Boolean(timedOut) : !this.timedOut;
			
			if (timedOut !== this.timedOut) {
				this.timedOut = timedOut;
				
				if (this.timedOut === true) {
					this.triggerTimedOutModal();
					this.onTimeout();
				}
			}
		},
		
		/**
		 * Triggers the timed out popup
		 */
		triggerTimedOutModal: function () {
			this.$timedOutModal.modal({
				backdrop: "static",
				show: true,
				keyboard: false
			});
		},
		
		onTimeout: function () {
			if (typeof this.onTimeoutCallback === "function") {
				this.onTimeoutCallback.call();
			}
		},
		
		unlock: function () {
			$.ajax({
				url: "",
				success: function (response) {
					
				},
				error: function () {
					
				}
			})
		},

		refreshLockRequest: function (editing) {
			var self = this;

			$.ajax({
				url: self.refreshUrl,
				type: "POST",
				data: {
					editing: Boolean(editing)
				},
				success: function (response) {
					self.setTimedOutState(!response.refreshed);
				},
				error: function () {
					console.log(arguments);
				}
			});
		},
		
		/**
		 * Pings to the server (browser window still open)
		 */
		ping: function () {
			if (this.isTimedOut()) {
				return false;
			}
			
			this.refreshLockRequest();
		},
		
		/**
		 * Sends a still active request to the server to prevent being timed out
		 */
		preventTimeout: function () {
			if (this.isTimedOut()) {
				return false;
			}
			
			this.refreshLockRequest(true);
			this.postponePing();
		}
	});

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

			this.$expansionIndicator = this.$(
					".js-module-title .js-expansion-indicator");
		},

		onExpand: function() {
			this.$expansionIndicator
				.removeClass("icon-chevron-right")
				.addClass("icon-chevron-down");
		},

		onCollapse: function() {
			this.$expansionIndicator
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

			// Store this view instance against the series element to
			// access it from hashchanges below.q
			this.$el.data("view", this)

			listEvents.on("expand-series", this.onExpandSeries);
		},

		isLoaded: function() {
			return this.$("table").length > 0;
		},

		isLoading: function() {
			return this.$(".js-loading-indicator").length > 0;
		},

		getSeriesId: function() {
			return this.$el.data("id");
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
			this.buildEventViews();
			listEvents.trigger("new-events-visible");
		},

		buildEventViews: function() {
			// At this point the events exist in the page. Instanciate a 
			// EventView wrapping each event and store the list of these
			// views in this.eventsd
			this.events = _.map(this.$(".js-event"), function(eventEl) {
				var eventView = new EventView({el: eventEl});

				return eventView;
			}, this);
		},

		onEventsFetchFailed: function() {
			this.loadingIndicator.showErrorState();
		},

		onExpand: function(event) {
			event.stopPropagation();

			this.$(".js-expansion-indicator")
				.removeClass("icon-chevron-right")
				.addClass("icon-chevron-down");

			if(this.isLoaded() || this.isLoading()) {
				return;
			}

			this.loadEvents();
		},

		onCollapse: function(event) {
			event.stopPropagation();
			this.$(".js-expansion-indicator")
				.removeClass("icon-chevron-down")
				.addClass("icon-chevron-right");
			this.$(".js-events").removeClass("shown");
		},

		onShown: function() {
			this.$(".js-events").addClass("shown");
		},

		/**
		 * Show the series, expanding the events list and triggering
		 * a fetch of events of events if required.
		 */
		expand: function() {
			this.$(".js-events").collapse("show");
		},

		onExpandSeries: function(id) {
			if(this.getSeriesId() == id)
				this.expand();
		}
	});
	
	var WritableModuleView = ModuleView.extend({
		constructor: function WritableModuleView () {
			WritableModuleView.__super__.constructor.apply(this, arguments);
		},
		
		initialize: function () {
			//apply initialization of superclass
			WritableModuleView.__super__.initialize.apply(this, arguments);
			
			this.editableTitle = new EditableTitleView({
				el: this.$(".js-module-title h4"),
				$toggleButton: this.$(".js-module-buttons .js-edit-icon"),
				titleFieldName: "fullname"
			});
		},
		
		lock: function () {
			this.locked = true;
			this.editableTitle.lock();
		}
	});

	var WritableSeriesView = SeriesView.extend({
		constructor: function WritableSeriesView() {
			WritableSeriesView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			var superEvents = WritableSeriesView.__super__.events.call(this);
			
			return _.extend(superEvents, {
				"click .js-btn-cancel": this.onCancel,
				"click .js-btn-save": this.onSave,
				"click .js-btn-add-event": this.onAddEvent
			});
		},
		
		lock: function () {
			this.locked = true;
			this.editableTitle.lock();
		},

		initialize: function() {
			WritableSeriesView.__super__.initialize.apply(this, arguments);
			this.editableTitle = new EditableTitleView({
				el: this.$(".js-series-title h5"),
				$toggleButton: this.$(".js-series-buttons .js-edit-icon"),
				titleFieldName: "title"
			});
			this.currentChangesState = false;
			_.bindAll(this);
		},

		getEventsRequestOptions: function() {
			var baseOptions = WritableSeriesView.__super__
				.getEventsRequestOptions();

			return _.extend(baseOptions, {
				data: {writeable: true}
			});
		},

		buildEventViews: function() {
			// At this point the events exist in the page. Instanciate a 
			// WritableEventView wrapping each event and store the list
			// of these views in this.events
			this.events = _.map(this.$(".js-event"), function(eventEl) {
				var eventView = new WritableEventView({el: eventEl});

				// Watch for events being modified
				eventView.on("event:savedStatusChanged", this.onSavedStatusChanged);
				eventView.on("datetimedialogopen", this.onDateTimeOpen);
				eventView.on("datetimedialogclose", this.onDateTimeClose);

				return eventView;
			}, this);

			this.$cancelSaveBtns = this.$(".js-save-cancel-btns");
		},

		onDateTimeOpen: function () {
			this.$(".js-btn-save").toggleClass("btn-success", false).css({
				opacity: .3
			});

			this.$(".js-btn-cancel").css({
				opacity: .3
			});
		},

		onDateTimeClose: function () {
			this.$(".js-btn-save").toggleClass("btn-success", true).css({
				opacity: 1
			});

			this.$(".js-btn-cancel").css({
				opacity: 1
			});
		},

		onSavedStatusChanged: function() {
			// Check for any events being changed and hide/show cancel/save
			// button as needed.
			var changesExist = _.any(this.events, function(event) {
				return event.model.hasChangedFromOriginal();
			});

			// Make the cancel/save buttons visible/hidden as required
			if (changesExist !== this.currentChangesState) {
				if (changesExist === true) {
					this.$cancelSaveBtns.stop().hide().slideDown(200);
				} else {
					this.$cancelSaveBtns.stop().show().slideUp(200);
				}
				
				this.currentChangesState = changesExist;
			}
		},

		onCancel: function(event) {
			_.each(this.events, function(eventView) {
				eventView.cancelChanges();
				// This works, but is a bit hacky
				//eventView.unfocusForEditing();
			});
		},

		onSave: function(event) {
			console.log("save button clicked");
			if (this.locked === true) {
				return false;
			}
			// Build a JSON representation of the form. 

			var forms = _.map(this.events, function(eventView) {
				return eventView.model.asJSONDjangoForm();
			});

			var outerForm = {
				"event_set": {
					// can't add forms yet so this is OK
					"initial": forms.length,
					"forms": forms
				}
			};

			var formData = DjangoForms.encodeJSONForm(outerForm);

			// Create a modal dialog to prevent actions taking place while
			// saving.
			this.saveDialogView = new SaveEventsDialogView();
			this.saveDialogView.on("saved", this.onEventsSaved)

			// Show the dialog & kick off the form POST.
			this.saveDialogView.postEventsForm(this.getSavePath(), formData)
		},

		onEventsSaved: function(response) {
			delete this.saveDialogView;
			this.currentChangesState = false;
			this.$(".js-events").empty();
			this.onEventsFetched(response);
		},

		/** Gets the path to the endpoint the POST changes to when saving. */
		getSavePath: function() {
			return this.$el.data("save-path");
		},

		onAddEvent: function(event) {
			return false;
		}
	});

	var EventView = Backbone.View.extend({
		constructor: function EventView() {
			EventView.__super__.constructor.apply(this, arguments);
		},

		initialize: function() {
			_.bindAll(this);

			listEvents.on("highlight-event", this.onHighlight);
		},

		getId: function() {
			return this.$el.data("id");
		},

		onHighlight: function(id) {
			if(this.getId() == id)
				this.highlight();
		},

		highlight: function() {
			this.$el.addClass("highlighted");
			scrollTo(this.$el.offset().top - 100, 200);
		}
	});

	var EventModel = BaseModel.extend({
		constructor: function EventModel() {
			EventModel.__super__.constructor.apply(this, arguments);
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
		 * Get an object of model attributes matching the Django form fields
		 * accepted by the series edit endpoint.
		 */
		asJSONDjangoForm: function() {
			var attrs = this.attributes;

			// Map our field names onto the server's Django form field names
			return {
				id: attrs.id,
				title: attrs.title,
				location: attrs.location,
				event_type: attrs.type,
				people: attrs.people,
				term_week: safeParseInt(attrs.week),
				term_name: attrs.term,
				day_of_week: attrs.day,
				start_hour: safeParseInt(attrs.startHour),
				start_minute: safeParseInt(attrs.startMinute),
				end_hour: safeParseInt(attrs.endHour),
				end_minute: safeParseInt(attrs.endMinute),
				cancel: attrs.cancel
			};
		}
	});

	var WritableEventView = EventView.extend({
		constructor: function WritableEventView() {
			WritableEventView.__super__.constructor.apply(this, arguments);
		},

		initialize: function () {
			WritableEventView.__super__.initialize.apply(this, arguments);

			this.$titleField = this.$(".js-field-title");;
			this.$locationField = this.$(".js-field-location");
			this.$peopleField = this.$(".js-field-people");
			this.$typeField = this.$("select.js-field-type");

			this.$weekField = this.$(".js-field-week");
			this.$termField = this.$(".js-field-term");
			this.$dayField = this.$(".js-field-day");
			this.$startHourField = this.$(".js-field-start-hour");
			this.$startMinuteField = this.$(".js-field-start-minute");
			this.$endHourField = this.$(".js-field-end-hour");
			this.$endMinuteField = this.$(".js-field-end-minute");

			this.$typeWrapper = this.$(".js-event-type-input-wrap");
			this.$dateTimeWrapper = this.$(".js-date-time-cell");

			this.model = new EventModel();
			this.updateModel();
			this.model.storeInitialState();
			this.model.on("change", this.render);
		},

		updateModel: function() {
			// Update our model with the current state of the HTML
			this.model.set({
				id: safeParseInt(this.$el.data("id")),
				title: this.$titleField.text(),
				location: this.$locationField.text(),
				type: this.$typeField.val(),
				people: this.$peopleField.text(),
				week: this.$weekField.text(),
				term: this.$termField.text().toLowerCase(),
				day: this.$dayField.text().toLowerCase(),
				startHour: this.$startHourField.text(),
				startMinute: this.$startMinuteField.text(),
				endHour: this.$endHourField.text(),
				endMinute: this.$endMinuteField.text(),
				cancel: this.$el.hasClass("event-cancelled")
			});
		},

		render: function () {
			var isCancelled = this.isCancelled();

			this.setFieldValue(this.$titleField, this.model.get("title"));
			this.setFieldValue(this.$locationField, this.model.get("location"));
			this.setFieldValue(this.$peopleField, this.model.get("people"));

			this.setFieldValue(this.$weekField, this.model.get("week"));
			this.setFieldValue(this.$termField, this.model.getPrettyTerm());
			this.setFieldValue(this.$dayField, this.model.getPrettyDay());
			this.setFieldValue(this.$startHourField, this.model.get("startHour"));
			this.setFieldValue(this.$endHourField, this.model.get("endHour"));
			this.setFieldValue(this.$startMinuteField, this.model.get("startMinute"));
			this.setFieldValue(this.$endMinuteField, this.model.get("endMinute"));

			this.$typeField.val(this.model.get("type"));

			this.$titleField.attr("contenteditable", !isCancelled);
			this.$locationField.attr("contenteditable", !isCancelled);
			this.$peopleField.attr("contenteditable", !isCancelled);
			this.$typeField.attr("disabled", isCancelled);

			this.$el.toggleClass("event-cancelled", isCancelled);
		},

		isCancelled: function () {
			return this.model.get("cancel");
		},

		setFieldValue: function ($field, value) {
			if ($field.text() !== value) {
				$field.text(value);
			}
		},

		events: function () {
			return {
				"click .js-field-title, .js-field-location, .js-field-people" : this.editableFieldClickHandler,

				"focus .js-field-title" : this.titleFieldFocusHandler,
				"focus .js-field-location" : this.locationFieldFocusHandler,
				"focus .js-field-people" : this.peopleFieldFocusHandler,
				"focus .js-event-type-input-wrap" : this.typeWrapFocusHandler,
				"focus .js-date-time-cell" : this.dateTimeWrapFocusHandler,
				"click .js-date-time-cell" : this.dateTimeWrapFocusHandler,

				"focusout .js-field-title" : this.titleFieldFocusOutHandler,
				"focusout .js-field-location" : this.locationFieldFocusOutHandler,
				"focusout .js-field-people" : this.peopleFieldFocusOutHandler,
				"focusout select.js-field-type" : this.typeFieldFocusOutHandler,
				"focusout .js-date-time-cell" : this.dateTimeFocusOutHandler,

				"click .js-edit-icon" : this.editIconClickHandler,
				"click .js-remove-icon" : this.removeIconClickHandler,
				"focus *" : this.focusInHander,
				"focusout" : this.focusOutHandler,

				"keyup" : this.keyUpHandler,
				"change select, input" : this.changeHandler
			};
		},

		dateTimeFocusOutHandler: function (event) {
			var self = this;
			_.delay(function () {
				if (!self.$dateTimeWrapper.is(":active") && self.$dateTimeWrapper.find(":focus, :active").length < 1) {
					self.closeDateTimeDialog();
				}
			}, 50);
		},

		removeIconClickHandler: function (event) {
			this.toggleCancelledState();
			event.preventDefault();
		},

		keyUpHandler: function (event) {
			this.updateModel();
			this.markAsChanged();
		},

		changeHandler: function (event) {
			this.updateModel();
			this.markAsChanged();
		},

		cancelChanges: function () {
			this.model.reset();
			this.markAsChanged();
			this.$typeWrapper.removeClass("being-edited");
		},

		titleFieldFocusOutHandler: function (event) {
			this.$titleField.removeClass("being-edited");
		},

		locationFieldFocusOutHandler: function (event) {
			this.$locationField.removeClass("being-edited");
		},

		peopleFieldFocusOutHandler: function (event) {
			this.$peopleField.removeClass("being-edited");
		},

		typeFieldFocusOutHandler: function (event) {
			//check if value is different from original; remove being-edited class
			if (!this.model.hasFieldChangedFromOriginal("type")) {
				this.$typeWrapper.removeClass("being-edited");
			}
		},

		markAsChanged: function () {
			this.$el.toggleClass("unsaved", this.model.hasChangedFromOriginal());
			this.trigger("event:savedStatusChanged");
		},

		hasFocus: function () {
			return this.$el.find(":focus").length > 0 || this.$el.find(":active").length > 0;
		},

		focusOutHandler: function (event) {
			var self = this;
			this.caretMoved = false;
			_.delay(function () {
				if (!self.hasFocus()) {
					self.$el.removeClass("row-being-edited");
					self.toggleRowBeingEditedState(false);
				}
			}, 50);
		},

		focusInHander: function (event) {
			this.toggleRowBeingEditedState(true);
		},

		editIconClickHandler: function (event) {
			if (!this.isCancelled()) {
				this.$el.addClass("row-being-edited");
			}
		},

		dateTimeWrapFocusHandler: function (event) {
			this.toggleDateTimeDialog(true);
		},

		typeWrapFocusHandler: function (event) {
			if (this.$typeWrapper.hasClass("being-edited") === false) {
				this.$typeWrapper.addClass("being-edited");
				this.$typeField.focus();
			}
		},

		editableFieldClickHandler: function (event) {
			if (!this.caretMoved) {
				this.moveCaretToEndOfContenteditableElement(event.currentTarget);
				this.caretMoved = true;
			}
		},

		titleFieldFocusHandler: function (event) {
			var self = this;
			this.$titleField.addClass("being-edited");
			this.moveCaretToEndOfContenteditableElement(event.currentTarget);
		},

		locationFieldFocusHandler: function (event) {
			this.$locationField.addClass("being-edited");
			this.moveCaretToEndOfContenteditableElement(event.currentTarget);
		},

		peopleFieldFocusHandler: function (event) {
			this.$peopleField.addClass("being-edited");
			this.moveCaretToEndOfContenteditableElement(event.currentTarget);
		},

		moveCaretToEndOfContenteditableElement: function (contentEditableElement) {
			var range,selection;
			if (document.createRange) {
				range = document.createRange();
				range.selectNodeContents(contentEditableElement);
				range.collapse(false);
				selection = window.getSelection();
				selection.removeAllRanges();
				selection.addRange(range);
			} else if (document.selection) { //IE 8 and lower
				range = document.body.createTextRange();
				range.moveToElementText(contentEditableElement);
				range.collapse(false);
				range.select();
			}
		},

		toggleRowBeingEditedState: function (beingEdited) {
			beingEdited = typeof beingEdited !== "undefined" ? beingEdited : !this.$el.hasClass("being-edited");
			this.$el.toggleClass("being-edited", beingEdited);
		},

		closeDateTimeDialog: function (toggleRowBeingEditedState) {
			if (this.dateTimeDialog) {
				this.markAsChanged();
				this.dateTimeDialog.remove();
				delete this.dateTimeDialog;
				this.$dateTimeWrapper.find(".event-input").removeClass("being-edited");

				if (toggleRowBeingEditedState) {
					this.$(".js-edit-icon").focus().click();
				}

				this.trigger("datetimedialogclose");
			}
		},

		toggleCancelledState: function (cancelled) {
			cancelled = typeof cancelled !== "undefined" ? cancelled : !this.isCancelled();

			if (cancelled !== this.isCancelled()) {
				this.model.set("cancel", cancelled);
				this.markAsChanged();
				this.$('[contenteditable="true"]').blur()
			}
		},

		toggleDateTimeDialog: function(showDialog) {
			showDialog = typeof showDialog !== "undefined" ? showDialog : typeof this.dateTimeDialog === "undefined";

			if (this.isCancelled()) {
				return false;
			}

			if(showDialog === false) {
				this.closeDateTimeDialog();
				this.$dateTimeWrapper.find(".event-input").removeClass("being-edited");
			} else if (!this.dateTimeDialog) {
				this.dateTimeDialog = new DateTimeDialogView({
					el: $("#templates .js-date-time-dialog").clone(),
					model: this.model,
					toggleRowBeingEditedStateOnClose: this.$el.hasClass("row-being-edited")
				});
				// dialog:close is fired by the dialog when a click is made
				// outside its area, or the close icon is clicked.
				this.dateTimeDialog.on("dialog:close", this.closeDateTimeDialog);

				this.$(".js-date-time-cell .js-dialog-holder").append(this.dateTimeDialog.$el);
				this.dateTimeDialog.$el.show();
				this.dateTimeDialog.$el.find("#date-time-week").focus();

				this.$dateTimeWrapper.find(".event-input").addClass("being-edited");

				this.trigger("datetimedialogopen");
			}
		},
	});

	var EditableTitleView = Backbone.View.extend({
		initialize: function (opts) {
			_.bindAll(this, "onToggleClick");

			this.$toggleButton = opts.$toggleButton;
			this.titleFieldName = opts.titleFieldName || "title";

			this.$value = this.$(".js-value");
			
			this.model = new TitleModel({
				titleFieldName: opts.titleFieldName
			});
			
			this.isEditable = false;
			this.isSaving = false;
			this.isError = false;
			this.updateModel();
			this.model.storeInitialState();

			this.$toggleButton.on("click", this.onToggleClick);
		},
		
		lock: function () {
			this.locked = true;
		},

		onToggleClick: function (event) {
			if (this.isSaving === false && this.isEditable === false) {
				this.toggleEditableState();
			}

			event.preventDefault();
		},

		render: function () {
			this.$value.text(this.model.get(this.titleFieldName));
			this.$value.attr("contenteditable", this.isEditable).toggleClass("editable", this.isEditable).toggleClass("saving", this.isSaving).focus();
			this.$(".js-error-message").toggle(this.isError);
		},

		events: {
			"click a" : "onClick",
			"keydown .js-value" : "onKeyDown",
			"focusout .js-value" : "onFocusOut"
		},

		onKeyDown: function (event) {
			if (event.keyCode === 13 && this.isEditable === true) {
				this.saveAndClose();
				event.preventDefault();
			}
		},

		onFocusOut: function (event) {
			if (this.isEditable === true) {
				this.saveAndClose();
			}
		},

		saveAndClose: function () {
			if (this.locked === true) {
				return false;
			}
			
			this.updateModel();
			this.toggleEditableState(false);

			if (this.model.hasChangedFromOriginal()) {
				this.saveData();
			}
		},

		saveData: function () {
			var self = this,
				beforeSavingTime = new Date(),
				timeDifference,
				timer;
			
			this.toggleSavingState(true);
			
			$.ajax({
				type: "POST",
				url: this.$value.data("save-path"),
				data: DjangoForms.encodeJSONForm(this.model.asJSONDjangoForm()),
				success: function (data) {
					timeDifference = new Date() - beforeSavingTime;
					timer = setTimeout(function () {
						self.toggleSavingState(false);
						self.toggleErrorState(false);
						self.$value.text(data[self.titleFieldName]);
						self.updateModel();
						self.model.storeInitialState(true);
					}, Math.max(200 - timeDifference, 0));
				},
				error: function () {
					timeDifference = new Date() - beforeSavingTime;
					timer = setTimeout(function () {
						self.model.reset();
						self.toggleSavingState(false);
						self.toggleErrorState(true);
					}, Math.max(200 - timeDifference, 0));
				}
			});
		},

		onClick: function (event) {
			if (this.isEditable === true) {
				event.stopPropagation();
			}
			
			event.preventDefault();
		},

		updateModel: function () {
			this.model.set(this.titleFieldName, this.$value.text());
		},
		
		toggleErrorState: function (isError) {
			isError = typeof isError !== "undefined" ? isError : !this.isError;
			
			if (isError !== this.isError) {
				this.isError = isError;
				this.render();
			}
		},

		toggleEditableState: function (isEditable) {
			isEditable = typeof isEditable !== "undefined" ? isEditable : !this.isEditable;

			if (isEditable !== this.isEditable) {
				this.isEditable = isEditable;
				this.render();
			}
		},
		
		toggleSavingState: function (isSaving) {
			isSaving = typeof isSaving !== "undefined" ? isSaving : !this.isSaving;

			if (isSaving !== this.isSaving) {
				this.isSaving = isSaving;
				this.render();
			}
		}
	});

	var DateTimeDialogView = Backbone.View.extend({
		constructor: function DateTimeDialogView() {
			DateTimeDialogView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"click .js-close-btn": this.onCloseClick,
				"click .js-ok-btn" : this.onOkClick,

				"change #date-time-week": this.onWeekChanged,
				"change .js-hour, .js-minute": this.onTimeInputChanged,
				"change select" : this.onSelectChange
			};
		},

		onSelectChange: function (event) {
			event.stopPropagation();
		},
 
		initialize: function(opts) {
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

			//initialize typeahead functionality for hour inputs
			this.initTypeAhead(this.$startHour, this.createHourArray());
			this.initTypeAhead(this.$endHour, this.createHourArray());

			//initialize typeahead functionality for minute inputs
			this.initTypeAhead(this.$startMinute, this.createMinuteArray());
			this.initTypeAhead(this.$endMinute, this.createMinuteArray());

			//show typeahead dropdown on focus:
			this.$startHour.on("focus", this.$startHour.typeahead.bind(this.$startHour, "lookup"));
			this.$endHour.on("focus", this.$endHour.typeahead.bind(this.$endHour, "lookup"));
			this.$startMinute.on("focus", this.$startMinute.typeahead.bind(this.$startMinute, "lookup"));
			this.$endMinute.on("focus", this.$endMinute.typeahead.bind(this.$endMinute, "lookup"));

			this.updateInitialTimeOffset();

			// Initialise the inputs
			this.render();
		},

		createMinuteArray: function () {
			var minuteArray = [],
				maxCount = 45,
				i = 0,
				iterator = 15;

			for (i; i <= maxCount; i += iterator) {
				var minuteString = String(i);

				if (minuteString.length === 1) {
					minuteString = "0" + minuteString
				}

				minuteArray.push(minuteString);
			}

			return minuteArray;
		},

		createHourArray: function () {
			var hourArray = [],
				maxCount = 24,
				i = 1,
				iterator = 1;

			for (i; i < maxCount; i += iterator) {
				var hourString = String(i);

				if (hourString.length === 1) {
					hourString = "0" + hourString;
				}

				hourArray.push(hourString);
			}

			return hourArray;
		},

		initTypeAhead: function ($el, source) {
			$el.typeahead({
				source: source,
				matcher: function () {
					return true;
				},
				sorter: function (items) {
					console.log(this);
					return items;
				},
				items: source.length
			});
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

		minutesFromTime: function(hours, minutes) {
			return (hours * 60) + minutes;
		},

		timeFromMinutes: function(minutes) {
			return [Math.floor(minutes / 60), minutes % 60];
		},

		getInitialTimeOffset: function () {
			return this.timeOffset;
		},

		updateInitialTimeOffset: function () {
			this.timeOffset = this.getCurrentTimeOffset();
		},

		getCurrentTimeOffset: function () {
			var fromTimeMinutes =  this.minutesFromTime(safeParseInt(this.$startHour.val()), safeParseInt(this.$startMinute.val())),
				toTimeMinutes = this.minutesFromTime(safeParseInt(this.$endHour.val()), safeParseInt(this.$endMinute.val())),
				offset = toTimeMinutes - fromTimeMinutes;
			return isNaN(offset) ? this.getInitialTimeOffset() : offset;
		},

		/**
		 * Convert number into a string, padding it to be minWidth wide by
		 * prefixing it with zeros.
		 */
		zeroPad: function(number, minWidth) {
			minWidth = minWidth || 2;
			var width;
			if(number == 0)
				width = 1;
			else
				width = Math.floor(Math.log(Math.abs(number)) / Math.LN10) + 1;

			return (number < 0 ? "-" : "")
					+ new Array(Math.max(0, minWidth - width) + 1).join("0")
					+ Math.abs(number);
		},

		onOkClick: function (event) {
			this.syncToModel();
			this.requestDialogClose();
			event.preventDefault();
		},
		
		onCloseClick: function (event) {
			this.requestDialogClose();
			event.preventDefault();
		},

		onWeekChanged: function() {
			// Reset week to the last good value if it's not an int
			if(isNaN(safeParseInt(this.$week.val())))
				this.$week.val(this.model.get("week"));

			//this.syncToModel();
		},

		onTimeInputChanged: function (event) {
			var startEdited = $(event.currentTarget).hasClass("js-start"),

				fromTotalMinutes = this.minutesFromTime(
					safeParseInt(this.$startHour.val()),
					safeParseInt(this.$startMinute.val())
				),

				toTotalMinutes = this.minutesFromTime(
					safeParseInt(this.$endHour.val()),
					safeParseInt(this.$endMinute.val())
				),

				fromTime,
				toTime;

			fromTotalMinutes = isNaN(fromTotalMinutes) ? 0 : fromTotalMinutes;
			toTotalMinutes = isNaN(toTotalMinutes) ? 0 : toTotalMinutes;

			if (startEdited === true) {
				toTotalMinutes += this.getInitialTimeOffset() - this.getCurrentTimeOffset();
				toTotalMinutes = Math.max(fromTotalMinutes + 1, toTotalMinutes);
			} else {
				fromTotalMinutes = Math.min(toTotalMinutes - 1, fromTotalMinutes);
				this.updateInitialTimeOffset();
			}

			//validating the times
			fromTotalMinutes = Math.min(((24 * 60) - 2), fromTotalMinutes);
			fromTotalMinutes = Math.max(1, fromTotalMinutes);

			toTotalMinutes = Math.min(((24 * 60) - 1), toTotalMinutes);
			toTotalMinutes = Math.max(2, toTotalMinutes);

			//converting minutes to [hour, minutes]
			fromTime = this.timeFromMinutes(fromTotalMinutes);
			toTime = this.timeFromMinutes(toTotalMinutes);

			//updating the input fields with the new values
			this.$startHour.val(this.zeroPad(fromTime[0], 2));
			this.$startMinute.val(this.zeroPad(fromTime[1], 2));

			this.$endHour.val(this.zeroPad(toTime[0], 2));
			this.$endMinute.val(this.zeroPad(toTime[1], 2));
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
			this.$(".js-minute.js-end").focus();
		},

		remove: function() {
			// Remove our backdrop element when we're removed.
			this.backdrop.remove();
			// Call the superclass's remove()
			DateTimeDialogView.__super__.remove.apply(this, arguments);
		},

		requestDialogClose: function() {
			this.trigger("dialog:close", this.options.toggleRowBeingEditedStateOnClose);
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

	var SaveEventsDialogView = Backbone.View.extend({
		constructor: function() {
			SaveEventsDialogView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"click .btn": this.dismissDialog
			};
		},

		initialize: function() {
			_.bindAll(this);

			this.setElement($("#templates .js-events-save-dialog")[0]);
			this.$(".js-body").hide();
			this.$(".js-body-saving").show();
		},

		showModal: function() {
			this.$el.modal({
				backdrop: "static",
				keyboard: false,
				show: true
			});
		},

		postEventsForm: function(url, eventsData) {
			this.showModal();

			$.ajax({
				url: url,
				type: "POST",
				data: eventsData
			}).done(this.onPOSTDone).fail(this.onPOSTFail)
		},

		onPOSTDone: function(response) {
			this.$(".js-body").hide();
			this.$(".js-body-success").show();
			this.trigger("saved", response);
		},

		onPOSTFail: function() {
			this.$(".js-body").hide();
			this.$(".js-body-error").show();
		},

		dismissDialog: function(event) {
			this.$el.modal("hide");
			this.trigger("close");
			event.preventDefault();
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

	var TitleModel = BaseModel.extend({
		constructor: function TitleModel() {
			TitleModel.__super__.constructor.apply(this, arguments);
		},
		
		initialize: function (opts) {
			TitleModel.__super__.initialize.apply(this, arguments);
			this.titleFieldName = opts.titleFieldName || "title";
		},

		asJSONDjangoForm: function () {
			var attrs = this.attributes,
				returnObj = {};
			
			returnObj[this.titleFieldName] = attrs[this.titleFieldName];
			return returnObj;
		}
	});

	/**
	 * Scroll the window so that the top is at the specified vertical
	 * position on the page.
	 */
	function scrollTo(position, duration, onComplete) {
		duration = duration || 0;
		$('html, body').animate({
			scrollTop: $(".js-event").offset().top - 100
		}, duration, "swing", onComplete);
	}

	/** Return value wrapped in an array if it's not an array. */
	function asArray(value) {
		if(_.isArray(value))
			return value;
		return [value];
	}

	function highlightEventsInHash() {
		var highlight = asArray($.bbq.getState("highlight"));
		_.each(highlight, function(id) {
			id = parseInt(id);
			if(isNaN(id))
				return;
			highlightEvent(id);
		})
	}

	function highlightEvent(id) {
		listEvents.trigger("highlight-event", id);
	}

	/**
	 * Use jQuery bbq to watch for hashchange events & take appropreate
	 * actions. We support the following hash params:
	 *
	 * - expand=SERIES_ID
	 * - highlight=EVENT_ID
	 *
	 * Together these can be used to expand a series automatically and
	 * scroll to the specified event.
	 */
	function bindUrlHashWatcher() {
		$(window).bind("hashchange", function(e) {
			var state = $.bbq.getState();

			var expand = asArray($.bbq.getState("expand"));
			_.each(expand, function(seriesId) {
				// Sanitise ID
				var id = parseInt(seriesId)
				if(isNaN(id))
					return;

				// Fire the expand-series event
				listEvents.trigger("expand-series", id);
			});

			highlightEventsInHash();
		});
	}

	// This is fired when new events are added to the page.
	listEvents.on("new-events-visible", highlightEventsInHash);
	//listEvents.on("page-edited", locker.preventTimeout);

	return {
		ModuleView: ModuleView,
		SeriesView: SeriesView,
		WritableSeriesView: WritableSeriesView,
		WritableModuleView: WritableModuleView,
		bindUrlHashWatcher: bindUrlHashWatcher,
		Locker: Locker,
		listEvents: listEvents
	};
});

