define([
    "jquery",
    "underscore",
    "backbone",
    "util/django-forms",
    "jquery-bbq",
    "bootstrapTypeahead"
], function($, _, Backbone, DjangoForms) {
    "use strict";

    var listEvents = _.extend({}, Backbone.Events);

    /** Strip leading zeros from an integer such as: 01, 05, 005 etc. */
    function stripZeros(str) {
        var groups = /(-*)0*(\d+)/.exec(str);
        if (!groups) {
            return undefined;
        }

        var integer = groups[2];
        if(groups[1] === "-") { // handle negative values
            integer = -integer;
        }
        return integer;
    }

    /** As parseInt() except handles strings with leading zeros correctly. */
    function safeParseInt(str) {
        return parseInt(stripZeros(str), 10);
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
                throw new Error("No initial state set.");
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
            timedOut = typeof timedOut !== "undefined" ? Boolean(timedOut) : !this.timedOut;

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
                success: function () {

                },
                error: function () {

                }
            });
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

            this.model = new BaseModel();
            this.model.set({
                series: [],
                newSeries: []
            });

            this.$expansionIndicator = this.$(".js-module-title .js-expansion-indicator");
            this.createInitialSeriesViews();
        },

        createInitialSeriesViews: function () {
            var series = [],
                newSeriesView,
                self = this;

            this.$(".js-series").each(function() {
                newSeriesView = new SeriesView({el: this});
                newSeriesView.on("expand", self.onSeriesExpand);
                series.push(newSeriesView);
            });

            this.model.set("series", series);
        },

        onSeriesExpand: function () {
            this.$(".js-module-content").collapse("show");
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
                "hide .js-events": this.onCollapse
            };
        },

        initialize: function() {
            _.bindAll(this);

            // Store this view instance against the series element to
            // access it from hashchanges below.q
            this.$el.data("view", this);

            this.model = new BaseModel();

            listEvents.on("expand-series", this.onExpandSeries);
        },

        isLoaded: function() {
            return this.$el.data("loaded");
            // Old: empty series are possible!
            //return this.$("table").length > 0;
        },

        setLoaded: function (loaded) {
            this.$el.data("loaded", Boolean(loaded));
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
            this.setLoaded(true);
        },

        buildEventViews: function() {
            // At this point the events exist in the page. Instanciate a 
            // EventView wrapping each event and store the list of these
            // views in this.model.events
            var events = _.map(this.$(".js-event"), function(eventEl) {
                var eventView = new EventView({el: eventEl});
                return eventView;
            }, this);

            this.model.set("events", events);
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
            this.trigger("expand");
        },

        onExpandSeries: function(id) {
            if (this.getSeriesId() === id) {
                this.expand();
            }
        }
    });

    var WritableModuleView = ModuleView.extend({
        constructor: function WritableModuleView () {
            WritableModuleView.__super__.constructor.apply(this, arguments);
        },

        initialize: function () {
            _.bindAll(this);

            // Apply initialization of superclass
            WritableModuleView.__super__.initialize.apply(this, arguments);

            // Initialize the editableTitle view
            this.editableTitle = new EditableTitleView({
                el: this.$(".js-module-title h4"),
                $toggleButton: this.$(".js-module-buttons .js-edit-icon"),
                titleFieldName: "fullname"
            });

            // Bind extra event listeners and hide buttons we don't need if the
            // module is new
            if (this.options.added === true) {
                this.editableTitle.on("close", this.onTitleClose);
                this.editableTitle.on("save", this.onTitleSaveSuccess);
                this.$(".js-module-buttons").hide();
            }
        },

        /**
         * Function that creates seriesViews for each series found within the
         * module (based on the markup ".js-series".each)
         */
        createInitialSeriesViews: function () {
            var series = [],
                newSeriesView,
                self = this;

            // Create a WritableSeriesView for each series found within the
            // module
            this.$(".js-series").each(function() {
                newSeriesView = new WritableSeriesView({el: this});
                newSeriesView.on("expand", self.onSeriesExpand);
                series.push(newSeriesView);
            });

            // Save the series array in the model
            this.model.set("series", series);

            // If the module doesn't contain any series, check for series being
            // added to show/hide the "This module contains no series text"
            // paragraph
            if (!series.length) {
                this.model.on("change:newSeries", this.onNewSeriesChanged);
            }
        },

        /**
         * Triggered when the newSeries array in the model has changed. Check
         * whether there are events in the module and show/hide the no-series
         * text accordingly.
         */
        onNewSeriesChanged: function () {
            // Toggle the "This module contains no series text" based on whether
            // series have been added or not.
            this.$(".js-no-series").toggle(!Boolean(this.model.get("newSeries").length));
        },

        events: function() {
            // Extend (don't overwrite) the events defined in the superclass
            var superEvents = WritableModuleView.__super__.events.call(this);

            return _.extend(superEvents, {
                "click .js-btn-add-series": this.onAddSeriesClick
            });
        },

        onAddSeriesClick: function (event) {
            this.appendNewSeries();
            event.preventDefault();
        },

        /**
         * Adds a new series to the module. Binds all necesary listeners, saves
         * it in the model, etc.
         */
        appendNewSeries: function () {
            var $markup = $($("#js-templ-new-series").html()),
                newSeriesView = new WritableSeriesView({
                    el: $markup,
                    added: true
                });

            newSeriesView.on("expand", this.onSeriesExpand);
            this.$(".js-series-list").prepend($markup);

            this.model.set({
                newSeries: this.model.get("newSeries").concat(newSeriesView)
            });

            newSeriesView.editableTitle.toggleEditableState(true);
            newSeriesView.on("destroy", this.onSeriesRemoved);
        },

        onSeriesRemoved: function (removedSeriesView) {
            this.removeSeriesView(removedSeriesView);
        },

        /**
         * Removes a seriesView from the our model.
         */
        removeSeriesView: function (seriesView) {
            // Determine which array to remove the seriesView from.
            var target = seriesView.options.added === true ? "newSeries" : "series";
            this.model.set(target, _.without(this.model.get(target), seriesView));
        },

        /**
         * Triggered when the module has been successfully saved.
         */
        onTitleSaveSuccess: function (id, savePath) {
            // At this point we don't need these events anymore:
            this.editableTitle.off("save");
            this.editableTitle.off("close");

            // Do everything needed to successfully track the new module from
            // here.
            this.appendModuleContent();
            this.editableTitle.setSavePath(savePath);
            this.makeCollapsible(id);
        },

        /**
         * Function that makes the module collapsible (show/hide the series).
         * This is used for modules which have been added by the user, expects a
         * module id.
         */
        makeCollapsible: function (id) {
            var idString = "module-" + id + "-content";
            this.$(".js-collapse").attr({
                "data-target": "#" + idString,
                "data-toggle": "collapse"
            });

            this.$(".js-module-content").attr("id", idString);
        },

        /**
         * Gets the html from the module content template and appends it to the 
         * module. This is only used by new modules added by the user and is
         * triggered when the modules have been succesfully created in the
         * back-end (== title saved).
         */
        appendModuleContent: function () {
            var $newModuleContent = $($("#js-templ-new-module-content").html());
            this.$el.append($newModuleContent);
        },

        /**
         * Triggered when the title edit field has been closed. No async 
         * requests have happened at this point yet.
         */
        onTitleClose: function (value) {
            if (value === "") {
                this.destroy();
                return;
            }

            this.$(".js-module-buttons").show();
        },

        /**
         * Removes all event listeners from this series and the editableTitle
         * and removes all elements.
         */
        destroy: function () {
            this.editableTitle.off();
            this.editableTitle.remove();
            this.remove();
            this.trigger("destroy", this);
            this.off();
        },

        lock: function () {
            this.locked = true;
            this.editableTitle.lock();

            // Also lock the series.
            _.invoke(this.series, "lock");
            _.invoke(this.newSeries, "lock");
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

            // Bind extra event listeners and hide buttons if the module is new
            if (this.options.added === true) {
                this.editableTitle.on("close", this.onTitleClose);
                this.editableTitle.on("save", this.onTitleSaveSuccess);
                this.$(".js-series-buttons").hide();
            }

            // Bind a change handler to the model
            this.model.on("change", this.onSavedStatusChanged);

            _.bindAll(this);
        },

        /**
         * Function that runs when the title for a new series has been 
         * successfully saved.
         */
        onTitleSaveSuccess: function (id, titleSavePath, eventsSavePath) {
            // At this point we don't need these events anymore:
            this.editableTitle.off("save");
            this.editableTitle.off("close");

            // Do everything needed to successfully track the new series from
            // here.
            this.$el.data("id", id);
            this.appendSeriesContent();
            this.makeCollapsible(id);
            this.editableTitle.setSavePath(titleSavePath);
            this.setSavePath(eventsSavePath);

            // Perhaps not the prettiest but does what we want:
            // Triggers the code that runs when events for a series are fetched.
            // We can immediately run it here because this is a new series which
            // doesn't contain any events yet.
            this.onEventsFetched();
        },

        /**
         * Function that makes the series collapsable (show/hide the events).
         * This is used for series which have been added by the user, expects a
         * series id.
         */
        makeCollapsible: function (id) {
            var idString = "series-" + id + "-events";

            // Using $.data doesn't seem to work, bootstrap doesn't pick it up,
            // $.attr("data-*") however, seems to work perfectly fine.
            this.$(".js-collapse").attr({
                "data-toggle": "collapse",
                "data-target": "#" + idString
            });

            this.$(".js-events").attr("id", idString);
        },

        /**
         * Gets the html from the series content template and appends it to the 
         * series. This is only used by new series added by the user and is
         * triggered when the series have been succesfully created in the
         * back-end (== title saved).
         */
        appendSeriesContent: function () {
            var $seriesContent = $($("#js-templ-new-series-content").html());
            console.log("append series content", $seriesContent);
            this.$el.append($seriesContent);
        },

        onTitleClose: function (value) {
            if (value === "") {
                this.destroy();
                return;
            }

            this.$(".js-series-buttons").show();
        },

        /**
         * Removes all event listeners from this series and the editableTitle
         * and removes all elements.
         */
        destroy: function () {
            this.editableTitle.off();
            this.editableTitle.remove();
            this.remove();
            this.trigger("destroy", this);
            this.off();
        },

        getEventsRequestOptions: function() {
            var baseOptions = WritableSeriesView.__super__.getEventsRequestOptions();

            return _.extend(baseOptions, {
                data: {
                    writeable: true
                }
            });
        },

        buildEventViews: function() {
            // At this point the events exist in the page. Instantiate a 
            // WritableEventView wrapping each event and store the list
            // of these views in this.model.events
            var events = _.map(this.$(".js-event"), this.buildSingleEventView, this);

            this.model.set({
                currentChangesState: false,
                events: events,
                newEvents: [],
                initialEventsCount: events.length
            });

            this.$cancelSaveBtns = this.$(".js-save-cancel-btns");
        },

        /**
         * Function that wraps a single provided element in a writableEventView
         * view and binds all necessary events to it. 
         */
        buildSingleEventView: function (el) {
            var eventView = new WritableEventView({
                el: el
            });

            // Watch for events being modified
            eventView.on("event:savedStatusChanged", this.onSavedStatusChanged);
            eventView.on("datetimedialogopen", this.onDateTimeOpen);
            eventView.on("datetimedialogclose", this.onDateTimeClose);

            return eventView;
        },

        onDateTimeOpen: function () {
            this.$(".js-btn-save").toggleClass("btn-success", false).css({
                opacity: 0.3
            });

            this.$(".js-btn-cancel").css({
                opacity: 0.3
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

        /**
         * Checks if there are any changes in the series, shows/hides the save
         * and cancel buttons appropriately.
         */
        onSavedStatusChanged: function() {
            // Check for changes in the events or if any new events are being
            // added.
            var changesExist = _.any(this.model.get("events"), function(event) {
                return event.model.hasChangedFromOriginal();
            }) || this.model.get("newEvents").length > 0;

            // Make the cancel/save buttons visible/hidden as required
            if (changesExist !== this.model.get("currentChangesState")) {
                if (changesExist === true) {
                    this.$cancelSaveBtns.stop().hide().slideDown(200);
                } else {
                    this.$cancelSaveBtns.stop().show().slideUp(200);
                }

                this.model.set({
                    currentChangesState: changesExist
                });
            }

            this.$el.toggleClass("hasChanges", changesExist);
        },

        onCancel: function() {
            // Set each event to its original state (= undoing all the changes)
            _.each(this.model.get("events"), function(eventView) {
                eventView.cancelChanges();
            });

            // Remove any eventviews that were added by the user
            _.each(this.model.get("newEvents"), function (eventView) {
                eventView.remove();
            });

            // Reset the newEvents array
            this.model.set("newEvents", []);
        },

        onSave: function() {
            if (this.locked === true) {
                return false;
            }
            // Build a JSON representation of the form. 

            var initialEventForms = _.map(this.model.get("events"), function(eventView) {
                return eventView.model.asJSONDjangoForm();
            });

            var newEventForms = _.map(this.model.get("newEvents"), function (eventView) {
                return eventView.model.asJSONDjangoForm();
            });

            // Form data
            var outerForm = {
                "event_set": {
                    // The initial amount of events
                    "initial": initialEventForms.length,
                    // The total amount of events (initial + new)
                    "total": initialEventForms.length + newEventForms.length,
                    // The actual events data
                    "forms": initialEventForms.concat(newEventForms)
                }
            };

            var formData = DjangoForms.encodeJSONForm(outerForm);

            // Create a modal dialog to prevent actions taking place while
            // saving.
            this.saveDialogView = new SaveEventsDialogView();
            this.saveDialogView.on("saved", this.onEventsSaved);

            // Show the dialog & kick off the form POST.
            this.saveDialogView.postEventsForm(this.getSavePath(), formData);
        },

        /**
         * Function that removes all events and all event listeners attached to
         * them
         */
        clearEvents: function () {
            _.each(this.model.get("events").concat(this.model.get("newEvents")), function (eventView) {
                eventView.off();
                eventView.destroy();
            });

            this.model.set({
                events: [],
                newEvents: [],
                currentChangesState: false
            });
        },

        /**
         * Removes the saveDialog and events, triggers recreation of the events
         * based on the html response.
         */
        onEventsSaved: function(response) {
            delete this.saveDialogView;
            this.clearEvents();
            this.$(".js-events").empty();
            this.onEventsFetched(response);
        },

        /**
         * Sets the path to the endpoint to POST changes to
         */
        setSavePath: function (savePath) {
            this.$el.data("save-path", savePath);
        },

        /**
         * Gets the path to the endpoint the POST changes to when saving.
         */
        getSavePath: function() {
            return this.$el.data("save-path");
        },

        /**
         * Function that appends a new event row to the series table
         * @return [object] new row jQuery Object
         */
        appendNewEventRow: function () {
            var $eventRow;

            // If events already exist, clone the latest, else append an empty
            // row
            if (this.model.get("events").length) {
                $eventRow = this.$el.find(".js-event").last().clone();

                // If the event is cloned from one that already exists, we need
                // to remove the id attribute and add appropriate classes,
                // remove any buttons not used by new items.
                if (!$eventRow.hasClass("event-new")) {
                    $eventRow.addClass("event-new row-being-edited").removeAttr("data-id");

                    _.each($eventRow.find(".buttons a"), function (el) {
                        var $el = $(el);
                        if (!$el.hasClass("js-remove-icon")) {
                            $el.parent().remove();
                        }
                    });
                }
            } else {
                $eventRow = $($("#js-templ-new-event").html());
            }

            this.$el.find("tbody").append($eventRow);
            return $eventRow;
        },

        /**
         * Removes the deleted event from the newEvents array in our model
         */
        onNewEventRemoved: function (eventView) {
            // We have to get the array first, then modify (= remove the new
            // event) it and push it back into the model in order for the
            // Backbone model change events to be dispatched.
            this.model.set({
                newEvents: _.without(this.model.get("newEvents"), eventView)
            });
        },

        /**
         * Creates a new event row and its eventView wrapper when the "create
         * event" button is clicked, also adds it to the newEvents array in our
         * model.
         */
        onAddEvent: function(event) {
            var $newEvent,
                newEventView;

            $newEvent = this.appendNewEventRow();
            newEventView = this.buildSingleEventView($newEvent);

            // Add an event listener that listens to the new event being removed
            newEventView.on("destroyed", this.onNewEventRemoved);

            // We have to get the array first, then modify (= add the new event)
            // it and push it back into the model in order for the Backbone
            // model change events to be dispatched.
            this.model.set({
                newEvents: this.model.get("newEvents").concat(newEventView)
            });

            event.preventDefault();
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
            if (this.getId() === id) {
                this.highlight();
            }
        },

        highlight: function() {
            if (!this.$el.hasClass("highlighted")) {
                this.$el.addClass("highlighted");
                // Scroll to the highlighted element
                $("body, html").animate({
                    scrollTop: this.$el.offset().top - 100
                }, 300);
            }
        }
    });

    var EventModel = BaseModel.extend({
        constructor: function EventModel() {
            EventModel.__super__.constructor.apply(this, arguments);
        },

        titleCase: function(str) {
            if (str.length > 0) {
                return str[0].toUpperCase() + str.slice(1);
            }
            return str;
        },

        getPrettyTerm: function() {
            var term = this.get("term");
            if (term) {
                return this.titleCase(term);
            }
            return term;
        },

        getPrettyDay: function() {
            var day = this.get("day");
            if (day) {
                return this.titleCase(day);
            }
            return day;
        },

        validate: function() {
            /* Function disabled for now

            var errors = {};

            if (!attrs.title || attrs.title.trim() === "") {
                errors.title = ["This field is required."];
            }

            if (!attrs.type || attrs.type === "") {
                errors.type = ["This field is required."];
            }

            if (!attrs.location || attrs.location.trim() === "") {
                errors.location = ["This field is required."];
            }

            if (!attrs.people || attrs.people.trim() === "") {
                errors.people = ["This field is required."];
            }

            */
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
                title: attrs.title.trim(),
                location: attrs.location.trim(),
                event_type: attrs.type,
                people: attrs.people.trim(),
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

            this.$titleField = this.$(".js-field-title");
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
                // If no ID is specified, set as undefined (new event will be created in the backend when no ID is set)
                id: safeParseInt(this.$el.data("id")) || undefined,
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

        dateTimeFocusOutHandler: function () {
            var self = this;
            _.delay(function () {
                if (!self.$dateTimeWrapper.is(":active") && self.$dateTimeWrapper.find(":focus, :active").length < 1) {
                    self.closeDateTimeDialog();
                }
            }, 50);
        },

        destroy: function () {
            this.remove();
            this.trigger("destroyed", this);
        },

        removeIconClickHandler: function (event) {
            event.preventDefault();

            // If the item was an event being added by the user, simply remove
            // it and dispatch an event so the event series can lose track of it
            if (this.isNew()) {
                this.destroy();
                return;
            }

            // Else if the event was already present, toggle the cancelled state
            this.toggleCancelledState();
        },

        keyUpHandler: function () {
            this.updateModel();
            this.markAsChanged();
        },

        changeHandler: function () {
            this.updateModel();
            this.markAsChanged();
        },

        cancelChanges: function () {
            this.model.reset();
            this.markAsChanged();
            this.$typeWrapper.removeClass("being-edited");
        },

        titleFieldFocusOutHandler: function () {
            this.$titleField.removeClass("being-edited");
        },

        locationFieldFocusOutHandler: function () {
            this.$locationField.removeClass("being-edited");
        },

        peopleFieldFocusOutHandler: function () {
            this.$peopleField.removeClass("being-edited");
        },

        typeFieldFocusOutHandler: function () {
            //check if value is different from original; remove being-edited class
            if (!this.model.hasFieldChangedFromOriginal("type")) {
                this.$typeWrapper.removeClass("being-edited");
            }
        },

        isNew: function () {
            return this.model.get("id") === undefined;
        },

        markAsChanged: function () {
            this.$el.toggleClass("unsaved", this.model.hasChangedFromOriginal());
            this.trigger("event:savedStatusChanged");
        },

        hasFocus: function () {
            return this.$el.find(":focus").length > 0 || this.$el.find(":active").length > 0;
        },

        focusOutHandler: function () {
            var self = this;
            this.caretMoved = false;
            _.delay(function () {
                if (!self.hasFocus() && !self.isNew()) {
                    self.$el.removeClass("row-being-edited");
                    self.toggleRowBeingEditedState(false);
                }
            }, 50);
        },

        focusInHander: function () {
            this.toggleRowBeingEditedState(true);
        },

        editIconClickHandler: function () {
            if (!this.isCancelled()) {
                this.$el.addClass("row-being-edited");
            }
        },

        dateTimeWrapFocusHandler: function () {
            this.toggleDateTimeDialog(true);
        },

        typeWrapFocusHandler: function () {
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
                this.$("[contenteditable=\"true\"]").blur();
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
        }
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

        setSavePath: function (savePath) {
            this.$(".js-value").data("save-path", savePath);
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

        revert: function () {
            this.$value.text(this.model.get(this.titleFieldName));
        },

        onKeyDown: function (event) {
            // Nothing should happen if the title isn't in editable mode
            // (= has focus). This extra check was needed in some browsers.
            if (!this.isEditable) {
                return;
            }

            // If the escape key (27) is pressed the value should be reverted to
            // its previous state.
            // If the enter key (13) is pressed, the new value should be saved.
            switch (event.keyCode) {
            case 27:
                this.revert();
                /* falls through */
            case 13:
                this.$value.blur();
                event.preventDefault();
                break;
            }
        },

        onFocusOut: function () {
            if (this.isEditable === true) {
                this.saveAndClose();
                this.trigger("close", this.model.get(this.titleFieldName));
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
                        // TODO! remove placeholder id response from error func
                        //self.trigger("save", data.id);
                    }, Math.max(200 - timeDifference, 0));
                },
                error: function () {
                    timeDifference = new Date() - beforeSavingTime;
                    timer = setTimeout(function () {
                        // Pretend successful save
                        self.toggleSavingState(false);
                        self.toggleErrorState(false);
                        //self.$value.text(data[self.titleFieldName]);
                        self.updateModel();
                        self.model.storeInitialState(true);
                        self.trigger("save", Math.round(Math.random() * 99999), "/tripos/blablablaa");

                        /**
                         * Original:
                         *
                         * self.model.reset();
                         * self.toggleSavingState(false);
                         * self.toggleErrorState(true);
                         */
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

            //show typeahead dropdown on click
            this.$startHour.on("click", this.$startHour.typeahead.bind(this.$startHour, "lookup"));
            this.$endHour.on("click", this.$endHour.typeahead.bind(this.$endHour, "lookup"));
            this.$startMinute.on("click", this.$startMinute.typeahead.bind(this.$startMinute, "lookup"));
            this.$endMinute.on("click", this.$endMinute.typeahead.bind(this.$endMinute, "lookup"));

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
                    minuteString = "0" + minuteString;
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
            if (number === 0) {
                width = 1;
            } else {
                width = Math.floor(Math.log(Math.abs(number)) / Math.LN10) + 1;
            }

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
            if (isNaN(safeParseInt(this.$week.val()))) {
                this.$week.val(this.model.get("week"));
            }

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
            }).done(this.onPOSTDone).fail(this.onPOSTFail);
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

    /** Return value wrapped in an array if it's not an array. */
    function asArray(value) {
        if (_.isArray(value)) {
            return value;
        }
        return [value];
    }

    function highlightEventsInHash() {
        var highlight = asArray($.bbq.getState("highlight"));
        _.each(highlight, function(id) {
            id = parseInt(id, 10);
            if (isNaN(id)) {
                return;
            }
            highlightEvent(id);
        });
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
        $(window).bind("hashchange", function() {
            var expand = asArray($.bbq.getState("expand"));
            _.each(expand, function(seriesId) {
                // Sanitise ID
                var id = parseInt(seriesId, 10);
                if (isNaN(id)) {
                    return;
                }

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

