define([
    "jquery",
    "underscore",
    "backbone",
    "util/api-admin",
    "util/dialog-factory-admin",
    "util/django-forms",
    "util/focus-helper",
    "jquery-bbq",
    "util/jeditable-types",
    "bootstrapTypeahead",
    "util/underscore-mixins"
], function($, _, Backbone, api, dialogFactory, DjangoForms, focusHelper) {
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

        resetAttribute: function (key) {
            this.set(key, this.originalAttributes[key]);
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
         * Function that returns the set index from the initial attributes
         * object.
         */
        getInitialValue: function (index) {
            return this.originalAttributes[index];
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
            this.fullpath = opts.fullpath || "";

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

        refreshLockRequest: function (editing) {
            var self = this;
            api.refreshLock(this.fullpath, Boolean(editing), function (error, response) {
                if (error) {
                    console.log(arguments);
                    return;
                }

                self.setTimedOutState(!response.refreshed);
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
        events: function() {
            return {
                "show .js-module-content": this.onExpand,
                "hide .js-module-content": this.onCollapse,
                "shown .js-module-content": this.onShown,
                "focusin .js-module-title": this.onTitleFocusIn,
                "focusout .js-module-title": this.onTitleFocusOut
            };
        },

        onTitleFocusIn: function () {
            this.$(".js-module-title").addClass("focus");
        },

        onTitleFocusOut: function () {
            this.$(".js-module-title").removeClass("focus");
        },

        initialize: function() {
            _.bindAll(this, "onExpand", "onCollapse", "onTitleFocusIn", "onTitleFocusOut");

            this.model = new BaseModel();
            this.model.set({
                series: [],
                newSeries: []
            });

            this.$expansionIndicator = this.$(".js-module-title .js-expansion-indicator");
            this.createInitialSeriesViews();
        },

        /**
         * Function that creates seriesViews for each series found within the
         * module (based on the markup ".js-series".each)
         */
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
        events: function() {
            return {
                "show .js-events": this.onExpand,
                "shown .js-events": this.onShown,
                "hide .js-events": this.onCollapse,
                "focusin .js-series-title": this.onTitleFocusIn,
                "focusout .js-series-title": this.onTitleFocusOut
            };
        },

        onTitleFocusIn: function () {
            this.$(".js-series-title").addClass("focus");
        },

        onTitleFocusOut: function () {
            this.$(".js-series-title").removeClass("focus");
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

        getId: function() {
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

        startEventsRequest: function() {
            var self = this;
            this.loadingIndicator.showLoadingState();

            // make the ajax request to fetch the events
            api.getEvents(this.getId(), this instanceof WritableSeriesView, function (error, response) {
                if (error) {
                    self.onEventsFetchFailed();
                    return;
                }

                self.onEventsFetched(response);
            });
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
            if (this.getId() === id) {
                this.expand();
            }
        }
    });

    var WritableModuleView = ModuleView.extend({
        initialize: function () {
            _.bindAll(this);

            // Apply initialization of superclass
            WritableModuleView.__super__.initialize.apply(this, arguments);

            // Initialize the editableTitle view
            this.editableTitle = new EditableTitleView({
                el: this.$(".js-module-title h4"),
                $toggleButton: this.$(".js-module-buttons .js-edit-icon"),
                titleFieldName: "fullname",
                extraSaveData: this.options.extraSaveData
            });

            // Bind extra event listeners and hide buttons we don't need if the
            // module is new
            if (this.options.added === true) {
                this.editableTitle.on("cancel", this.onTitleCancel);
                this.editableTitle.on("save", this.onInitialTitleSaveSuccess);
                this.$(".js-module-buttons").hide();
                this.editableTitle.startEdit();
            }
            this.editableTitle.on("save", this.onTitleSaveSuccess);
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
                self.listenTo(newSeriesView, "expand", self.onSeriesExpand);
                self.listenTo(newSeriesView, "remove", self.onSeriesRemoved);
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
                "click .js-btn-add-series": this.onAddSeriesClick,
                "click .js-module-buttons .js-remove": this.onRemoveClick
            });
        },

        onAddSeriesClick: function (event) {
            this.appendNewSeries();
            event.preventDefault();
        },

        onRemoveClick: function (event) {
            // Remove the focus from the btn
            this.$(".js-module-buttons .js-remove").blur();
            this.showRemoveModal();
            event.preventDefault();
        },

        /**
         * Initialized the remove popup dialog and attaches all necessary
         * events.
         */
        showRemoveModal: function () {
            var data = {
                title: this.editableTitle.$value.text(),
                type: "module",
                totalSeries: this.getTotalSeries()
            };

            this.removeModal = dialogFactory.removeModule(data);
            this.listenTo(this.removeModal, "confirm", this.onRemoveModalConfirm);
            this.listenTo(this.removeModal, "close", this.onRemoveModalClose);
        },

        onRemoveModalClose: function () {
            focusHelper.focusTo(this.$(".js-module-buttons .js-remove"));
        },

        /**
         * When removal is confirmed by the user, do an ajax call to the server
         * to request the removal. Update the popup state based on the response
         * of the server (success or error).
         */
        onRemoveModalConfirm: function () {
            var self = this;
            this.removeModal.off("confirm");

            api.deleteModule(this.getId(), function (error) {
                if (error) {
                    self.removeModal.onError();
                    return;
                }

                self.removeModal.onSuccess();
                self.trigger("remove", self);
            });
        },

        /**
         * Adds a new series to the module. Binds all necesary listeners, saves
         * it in the model, etc.
         */
        appendNewSeries: function () {
            var $markup = $($("#js-templ-new-series").html()),
                newSeriesView;

            this.$(".js-series-list").prepend($markup);
            newSeriesView = new WritableSeriesView({
                el: $markup,
                added: true,
                extraSaveData: {
                    "id_parent": this.getId()
                }
            });

            this.listenTo(newSeriesView, "expand", this.onSeriesExpand);
            this.model.set({
                newSeries: this.model.get("newSeries").concat(newSeriesView)
            });

            this.listenTo(newSeriesView, "remove", this.onSeriesRemoved);
        },

        onSeriesRemoved: function (removedSeriesView) {
            this.removeSeriesView(removedSeriesView);
        },

        /**
         * Removes a seriesView from the our model.
         */
        removeSeriesView: function (seriesView) {
            // Determine which array to remove the seriesView from.
            var target = seriesView.options.added === true ? "newSeries" : "series",
                $focusTarget = seriesView.$el.prev().find(".js-edit-icon");
            this.model.set(target, _.without(this.model.get(target), seriesView));

            if (!$focusTarget.length) {
                $focusTarget = this.$(".js-btn-add-series");
            }

            seriesView.destroy();
            focusHelper.focusTo($focusTarget);
        },

        /**
         * Triggered when the module has been successfully saved.
         */
        onInitialTitleSaveSuccess: function (data) {
            // At this point we don't need these events anymore:
            this.editableTitle.off("save", this.onInitialTitleSaveSuccess);
            this.editableTitle.off("cancel");

            // Do everything needed to successfully track the new module from
            // here.
            this.appendModuleContent();
            this.makeCollapsible(data.id);
            this.setId(data.id);
            this.$(".js-module-buttons").show();
        },

        /**
         * Called when EditableTitleView has saved the module title. Saving
         * the title can update the fullpath, so we need to update the savepath
         * so that future edits go to the new link.
         */
        onTitleSaveSuccess: function (data) {
            this.editableTitle.setSavePath(data.save_path);
        },

        setId: function (id) {
            this.$el.data("id", id);
        },

        getId: function () {
            return this.$el.data("id");
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
         * Triggered when the title edit field has been cancelled (i.e. closed
         * without saving).
         */
        onTitleCancel: function () {
            this.trigger("remove", this);
        },

        /**
         * Removes all event listeners from this module along with the
         * editableTitle and all series/events found under the module.
         */
        destroy: function () {
            this.clearSeries();
            this.editableTitle.off();
            this.editableTitle.remove();
            this.remove();
            this.trigger("destroy", this);
            this.off();
        },

        getAllSeries: function () {
            var series = this.model.get("series"),
                newSeries = this.model.get("newSeries");

            if (series && newSeries) {
                return series.concat(newSeries);
            } else if (series) {
                return series;
            }

            return newSeries || [];
        },

        getTotalSeries: function () {
            return this.getAllSeries().length;
        },

        clearSeries: function () {
            _.invoke(this.getAllSeries(), "destroy");
        },

        lock: function () {
            this.locked = true;
            this.editableTitle.lock();

            // Also lock the series.
            _.invoke(this.getAllSeries(), "lock");
        }
    });

    var WritableSeriesView = SeriesView.extend({
        events: function() {
            var superEvents = WritableSeriesView.__super__.events.call(this);

            return _.extend(superEvents, {
                "click .js-btn-cancel": this.onCancel,
                "click .js-btn-save": this.onSave,
                "click .js-btn-add-event": this.onAddEvent,
                "click .js-remove": this.onRemoveClick
            });
        },

        lock: function () {
            this.locked = true;
            this.editableTitle.lock();
        },

        initialize: function() {
            _.bindAll(this);

            WritableSeriesView.__super__.initialize.apply(this, arguments);
            this.editableTitle = new EditableTitleView({
                el: this.$(".js-series-title h5"),
                $toggleButton: this.$(".js-series-buttons .js-edit-icon"),
                titleFieldName: "title",
                extraSaveData: this.options.extraSaveData
            });

            // Bind extra event listeners and hide buttons if the module is new
            if (this.options.added === true) {
                this.editableTitle.on("cancel", this.onTitleCancel);
                this.editableTitle.on("save", this.onTitleSaveSuccess);
                this.$(".js-series-buttons").hide();

                if (this.options.titleSavePath !== undefined) {
                    this.editableTitle.setSavePath(this.options.titleSavePath);
                }

                this.editableTitle.startEdit();
            }

            // Bind a change handler to the model
            this.model.on("change", this.onSavedStatusChanged);
        },

        setId: function (id) {
            this.$el.data("id", id);
        },

        /**
         * Function that runs when the title for a new series has been 
         * successfully saved.
         */
        onTitleSaveSuccess: function (data) {
            // At this point we don't need these events anymore:
            this.editableTitle.off("save");
            this.editableTitle.off("cancel");

            // Do everything needed to successfully track the new series from
            // here.
            this.appendSeriesContent();
            this.setId(data.id);
            this.makeCollapsible(data.id);
            this.editableTitle.setSavePath(data.url_edit_title);
            this.$(".js-series-buttons").show();

            // Perhaps not the prettiest but does what we want:
            // Triggers the code that runs when events for a series are fetched.
            // We can immediately run it here because this is a new series which
            // doesn't contain any events yet.
            this.onEventsFetched();
        },

        /**
         * Function that makes the series collapsible (show/hide the events).
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
            this.$el.append($seriesContent);
        },

        /**
         * Triggered when the title edit field has been cancelled (i.e. closed
         * without saving).
         */
        onTitleCancel: function () {
            this.trigger("remove", this);
        },

        /**
         * Removes all event listeners from this series and the editableTitle
         * and removes all elements.
         */
        destroy: function () {
            this.editableTitle.off();
            this.editableTitle.remove();
            this.clearEvents();
            this.remove();
            this.trigger("destroy", this);
            this.off();
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

        onRemoveClick: function (event) {
            // Remove the focus from the btn
            this.$(".js-remove").blur();
            this.showRemoveModal();
            event.preventDefault();
        },

        /**
         * Initialized the remove popup dialog and attaches all necessary
         * events.
         */
        showRemoveModal: function () {
            var data = {
                title: this.editableTitle.$value.text(),
                type: "series"
            };

            this.removeModal = dialogFactory.removeSeries(data);
            this.listenTo(this.removeModal, "confirm", this.onRemoveModalConfirm);
            this.listenTo(this.removeModal, "close", this.onRemoveModalClose);
        },

        /**
         * When removal is confirmed by the user, do an ajax call to the server
         * to request the removal. Update the popup state based on the response
         * of the server (success or error).
         */
        onRemoveModalConfirm: function () {
            var self = this;
            this.removeModal.off("confirm");

            api.deleteSeries(this.getId(), function (error) {
                if (error) {
                    self.removeModal.onError();
                    return;
                }

                self.removeModal.onSuccess();
                self.trigger("remove", self);
            });
        },

        onRemoveModalClose: function () {
            focusHelper.focusTo(this.$(".js-remove"));
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
            // Place the focus on the add event button
            focusHelper.focusTo(this.$(".js-btn-add-event"));
        },

        /**
         * Returns true if all data in the series is valid
         */
        isEventDataValid: function () {
            // Merge events and newevents arrays.
            var events = this.model.get("events").concat(this.model.get("newEvents"));
            // Check whether every model of each event contains valid data.
            return _.every(events, function (eventView) {
                return eventView.model.isValid();
            });
        },

        onSave: function() {
            if (this.locked === true) {
                return;
            }

            // Remove the focus from the save btn
            this.$(".js-btn-save").blur();

            // If the events data isn't valid, show a warning and abort saving.
            if (!this.isEventDataValid()) {
                var invalidDataDialog = dialogFactory.eventInvalidDataError();
                // Listen for the dialog close event to refocus on the save button
                this.listenTo(invalidDataDialog, "close", this.onInvalidDataDialogClose);
                return;
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
            this.saveDialogView.$el.on("hidden", this.onSaveDialogClose);
            this.saveDialogView.on("saved", this.onEventsSaved);

            // Show the dialog & kick off the form POST.
            this.saveDialogView.postEventsForm(this.getId(), formData);
        },

        onInvalidDataDialogClose: function () {
            focusHelper.focusTo(this.$(".js-btn-save"));
        },

        /**
         * Returns all events in the model (i.e. existing and new events). This
         * replaced .concat since concat fails when one of the arrays is
         * undefined.
         */
        getAllEvents: function () {
            var events = this.model.get("events"),
                newEvents = this.model.get("newEvents");

            if (events && newEvents) {
                return events.concat(newEvents);
            } else if (events) {
                return events;
            }

            return newEvents || [];
        },

        /**
         * Function that removes all events and all event listeners attached to
         * them
         */
        clearEvents: function () {
            _.each(this.getAllEvents(), function (eventView) {
                eventView.off();
                eventView.destroy();
            });

            this.model.set({
                events: [],
                newEvents: [],
                currentChangesState: false
            });
        },

        onSaveDialogClose: function () {
            this.saveDialogView.remove();
            delete this.saveDialogView;
            focusHelper.focusTo(this.$(".js-btn-add-event"));
        },

        /**
         * Removes the saveDialog and events, triggers recreation of the events
         * based on the html response.
         */
        onEventsSaved: function(response) {
            this.clearEvents();
            this.$(".js-events").empty();
            this.onEventsFetched(response);
        },

        /**
         * Function that appends a new event row to the series table
         * @return [object] new row jQuery Object
         */
        appendNewEventRow: function () {
            var $eventRow = $($("#js-templ-new-event").html());
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

            // Place the focus on the add event button
            focusHelper.focusTo(this.$(".js-btn-add-event"));
        },

        getNewEventInitialData: function () {
            // Gets initial data that can be used for new events by checking
            // the last event in the series. If the series is empty it'll return
            // an empty object.
            var newEvents = this.model.get("newEvents"),
                existingEvents = this.model.get("events");

            if (newEvents.length) {
                return _.last(newEvents).getFieldData();
            } else if (existingEvents.length) {
                return _.last(existingEvents).getFieldData();
            }

            return {};
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
            // Set the data of the new event view to the last event in the
            // series or blank if the series is empty.
            newEventView.model.set(this.getNewEventInitialData());
            newEventView.renderFromModel();

            // Open the event's edit state
            newEventView.openJEditableFields();
            newEventView.setRowEditState(true);
            focusHelper.focusTo(newEventView.$("input, textarea, select").first());

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

        /**
         * Checks whether the current data in the model is valid to save.
         * Currently only checks whether the title isn't empty or the default
         * value.
         */
        isValid: function () {
            // Lowercase the title before checking
            var cleanTitle = this.get("title").toLowerCase();
            return cleanTitle !== "" && cleanTitle !== "title";
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
        initialize: function () {
            WritableEventView.__super__.initialize.apply(this, arguments);

            // Initialize the model.
            this.model = new EventModel();
            // Save the current field values in the model
            this.syncModel();
            // Store the current state of the model so that we know when
            // changes have been made (to show/hide save/cancel buttons)
            this.model.storeInitialState();

            this.bindEvents();
            // Initialize the jeditable fields
            this.initJEditable();
        },

        events: function () {
            return {
                "keyup .tablecell-jeditable": this.onJEditableFieldInteraction,
                "paste .tablecell-jeditable": this.onJEditableFieldInteraction,
                "cut .tablecell-jeditable": this.onJEditableFieldInteraction,
                "change .type-select-jeditable": this.onJEditableFieldInteraction,

                "onreset .jeditable-field": this.onJEditableFieldReset,

                "click .js-date-time-cell": this.onDateTimeClick,
                "keydown .js-date-time-cell": this.onDateTimeKeyDown,

                "click .js-edit-icon": this.onEventEditClick,
                "click .js-remove-icon": this.onRemoveClick,

                "click td": this.onTableCellClick,
                "keyup .jeditable": this.onJEditableKeyup,
                "focusin": this.onFocusIn,
                "focusout": this.onFocusOut
            };
        },

        onTableCellClick: function (event) {
            var $target = $(event.target);
            // trigger a click on the field if the table cell is clicked
            if ($target.hasClass("event-field")) {
                var $inputElements = $target.find("input, textarea, select");
                if ($inputElements.length) {
                    focusHelper.focusTo($inputElements.first());
                    return;
                }
                $target.children().first().trigger("click");
            }
        },

        onJEditableKeyup: function (event) {
            var $target = $(event.currentTarget);

            // Only enter editable state when keys return (13) or space (32) are
            // pressed
            if (!$target.find("form").length && (event.keyCode === 13 || event.keyCode === 32)) {
                $target.trigger("click");
            }
        },

        onFocusIn: function () {
            this.$el.addClass("being-edited");
        },

        onFocusOut: function () {
            var self = this;
            _.defer(function () {
                if (!self.$el.find(":focus").length && !self.dateTimeDialog) {
                    self.$el.removeClass("being-edited");
                    // Close the row edit state if it's open
                    if (self.getRowEditState() && !self.isNew()) {
                        self.setRowEditState(false);
                        self.closeJEditableFields();
                    }
                }
            });
        },

        isNew: function () {
            // This function checks whether the event has an id. If it doesn't
            // it means that the event hasn't been saved yet.
            return !Boolean(this.getId());
        },

        setRowEditState: function (beingEdited) {
            this.$el.toggleClass("row-being-edited", beingEdited);
        },

        getRowEditState: function () {
            return this.$el.hasClass("row-being-edited");
        },

        closeJEditableFields: function () {
            _.each(this.getJEditableFields(), function (fieldData) {
                fieldData.$el.find("input, textarea, select").blur();
            });
        },

        openJEditableFields: function () {
            _.each(this.getJEditableFields(), function (fieldData) {
                fieldData.$el.trigger("click");
            });
        },

        onEventEditClick: function () {
            if (this.model.get("cancel")) {
                // Don't enter the edit state if the event is marked as
                // cancelled
                return;
            }

            var newEditState = !this.getRowEditState();
            // Set the new edit state on the element
            this.setRowEditState(newEditState);
            if (newEditState) {
                // If editState is set to true, trigger jeditable on all fields
                this.openJEditableFields();
                focusHelper.focusTo(this.$("input, textarea, select").first(), true);
                return;
            }
            // Else close them
            this.closeJEditableFields();
        },

        destroy: function () {
            this.destroyJEditableFields();
            this.remove();
            this.trigger("destroyed", this);
        },

        destroyJEditableFields: function () {
            // Trigger the jeditable destroy code
            _.each(this.getJEditableFields(), function (fieldData) {
                fieldData.$el.editable("destroy");
            });
        },

        onDateTimeClick: function () {
            if (!this.dateTimeDialog && !this.model.get("cancel")) {
                this.showDateTimeDialog();
            }
        },

        onDateTimeKeyDown: function (event) {
            if (this.dateTimeDialog) {
                // Close the dialog if escape (27) is pressed
                if (event.keyCode === 27) {
                    this.closeDateTimeDialog();
                }
                return;
            }

            // Open the date time dialog if the return key (13) or the space key
            // (32) is pressed
            if (!this.model.get("cancel") && (event.keyCode === 13 || event.keyCode === 32)) {
                this.showDateTimeDialog();
            }
        },

        onRemoveClick: function () {
            if (this.isNew()) {
                // If the event is new (not saved in the db) we can just remove it
                // from the ui
                this.destroy();
                return;
            }

            var model = this.model,
                // Save whether the event is currently cancelled before we reset
                // the model.
                currentlyCancelled = model.get("cancel");
            // Make sure the edit state is over
            this.setRowEditState(false);
            // Revert all open changes
            model.reset();
            // Set the appropriate cancelled value
            model.set("cancel", !currentlyCancelled);
            this.renderFromModel();
            // Close all jeditable fields
            this.closeJEditableFields();
        },

        showDateTimeDialog: function () {
            var dialog = new DateTimeDialogView({
                el: $("#templates .js-date-time-dialog").clone(),
                model: this.model
            });

            this.$(".js-date-time-input-wrap").addClass("being-edited");
            this.$(".js-date-time-cell .js-dialog-holder").append(dialog.$el);
            this.listenTo(dialog, "dialog:close", this.closeDateTimeDialog);
            dialog.show();

            this.dateTimeDialog = dialog;
        },

        closeDateTimeDialog: function () {
            var $dateTimeInputWrap = this.$(".js-date-time-input-wrap");
            // Update the elements with the values in the model
            this.renderFromModel();
            // Remove the dialog and the reference to it
            this.dateTimeDialog.remove();
            this.dateTimeDialog = undefined;
            $dateTimeInputWrap.removeClass("being-edited");
            focusHelper.focusTo($dateTimeInputWrap, true);
        },

        onJEditableFieldInteraction: function (event) {
            // Save the field's new value to our model.
            var $target = $(event.target);
            $target.parents(".js-field").data("value", $target.val());
            this.syncModel();
        },

        bindEvents: function () {
            this.listenTo(this.model, "change", this.onModelChange);
        },

        onModelChange: function (model) {
            // Mark the event as changed if the model has changed from its
            // original values.
            this.markAsChanged(model.hasChangedFromOriginal());
        },

        markAsChanged: function (changed) {
            // Update the classnames on the event to reflect whether the model
            // has changed from its original attributes. Also dispatch an event
            // to let the parent series know something has changed.
            var hasChangedState = this.$el.hasClass("unsaved");
            if (changed !== hasChangedState) {
                this.$el.toggleClass("unsaved", changed);
                this.trigger("event:savedStatusChanged");
            }
        },

        cancelChanges: function () {
            // Revert all the fields to their original values.
            this.model.reset();
            // Render the html based on what values are present in the model
            this.renderFromModel();
            // Reset all jeditable fields
            this.closeJEditableFields();
        },

        renderFromModel: function () {
            var model = this.model,
                cancelled = this.model.get("cancel");
            _.each(this.getFields(), function (fieldData) {
                var $jeditableField = fieldData.$el.find(".jeditable-field"),
                    value = model.get(fieldData.name),
                    // If this isn't a jeditable field, capitalize the value
                    // which will be shown to the user
                    textValue = fieldData.jeditable ? value : _.capitalize(value);

                // Only update if the value is different
                if (value !== fieldData.$el.data("value")) {
                    if ($jeditableField.length) {
                        // If there's a jeditable form element in the field, set its
                        // value to the model value
                        $jeditableField.find("input, select, textarea").val(value).trigger("resize");
                    } else {
                        // Else just update the element's text
                        if (fieldData.name === "type") {
                            // We have to fetch the presentational value if the
                            // field is the type select box
                            fieldData.$el.text(fieldData.data()[value]);
                        } else {
                            if (!textValue && fieldData.placeholder) {
                                // If the value is empty, we should show the
                                // placeholder if there is one available
                                fieldData.$el.text(fieldData.placeholder);
                            } else {
                                fieldData.$el.text(textValue);
                            }
                        }
                    }

                    // Also update the data-value attribute on the field element
                    fieldData.$el.data("value", value);
                }
            });

            this.$el.toggleClass("event-cancelled", cancelled);
            this.toggleJEditable(!cancelled);
        },

        toggleJEditable: function (enabled) {
            _.each(this.getJEditableFields(), function (fieldData) {
                fieldData.$el.editable(enabled ? "enable" : "disable");
            });
        },

        initJEditable: function () {
            // Initialize jeditable on fields which should have it enabled
            var jEditableFields = this.getJEditableFields(),
                self = this,
                // Define $focussedEl to keep track of ie8 focussed element
                $focussedEl;

            _.each(jEditableFields, function (fieldData) {
                fieldData.$el.editable(fieldData.onSubmitCallback || function (value) {
                    // Reset the element attributes to their original values
                    $(this).attr("tabindex", "0").removeClass("being-edited");
                    return value;
                }, _.defaults(fieldData, {
                    onblur: function () {
                        // Only close the form if row edit state is false, else
                        // we want to keep the fields open
                        if (!self.getRowEditState()) {
                            $(this).find("form").submit();
                        }
                    },
                    callback: (function () {
                        // If the browser is ie8, set a timeout to focus the
                        // element that was focussed before rendering the
                        // jeditable field. We have to do this because ie8
                        // removes focus from the element when the jeditable
                        // field is rendered.
                        if (focusHelper.isIE8()) {
                            return function () {
                                focusHelper.focusTo($focussedEl);
                            };
                        }
                        return;
                    }()),
                    onsubmit: (function () {
                        // If the browser is ie8, save a reference to the
                        // currently focussed element.
                        if (focusHelper.isIE8()) {
                            return function () {
                                $focussedEl = $(document.activeElement);
                            };
                        }
                        return;
                    }()),
                    select: true,
                    onreset: self.onJEditableFieldReset,
                    placeholder: fieldData.fieldName || _.capitalize(fieldData.name),
                    cssclass: fieldData.type + "-jeditable jeditable-field"
                }));
            });
        },

        getEventGeneralData: function () {
            return {
                id: this.$el.data("id") || undefined,
                cancel: this.$el.hasClass("event-cancelled")
            };
        },

        getFieldData: function () {
            var data = {};
            _.each(this.getFields(), function (fieldData) {
                // Convert to string to prevent type issues
                data[fieldData.name] = String(fieldData.$el.data("value"));
            });
            return data;
        },

        getEventData: function () {
            // Return the field values in an object format.
            return _.extend(this.getEventGeneralData(), this.getFieldData());
        },

        onJEditableFieldReset: function (event, el) {
            // Don't allow fields to be reset if this is a new event
            if (this.isNew()) {
                return false;
            }

            // Also stop row editing
            this.setRowEditState(false);
            // Reset the attribute in the model
            this.model.resetAttribute(event.name);
            this.renderFromModel();
            this.closeJEditableFields();
            focusHelper.focusTo(el);
            // jEditable doesn't have to update the attribute anymore:
            return false;
        },

        getFields: function () {
            var self = this;
            if (!this.fields) {
                this.fields = [
                    {
                        name: "title",
                        $el: this.$(".js-field-title"),
                        type: "tablecell",
                        jeditable: true,
                        maxLength: 200
                    },
                    {
                        name: "location",
                        $el: this.$(".js-field-location"),
                        type: "tablecell",
                        jeditable: true,
                        maxLength: 200
                    },
                    {
                        name: "people",
                        fieldName: "Lecturer",
                        $el: this.$(".js-field-people"),
                        type: "tablecell",
                        jeditable: true,
                        maxLength: 200
                    },
                    {
                        name: "type",
                        $el: this.$(".js-field-type"),
                        type: "type-select",
                        onSubmitCallback: function (value, settings) {
                            $(this).removeClass("being-edited").attr("tabindex", "0");
                            return settings.data()[value];
                        },
                        data: function () {
                            return $(".js-individual-modules").data("event-type-choices");
                        },
                        jeditable: true,
                        onblur: function (value, fieldData) {
                            if (!self.model.hasFieldChangedFromOriginal(fieldData.name) && !self.getRowEditState()) {
                                $(this).find("form").submit();
                            }
                        }
                    },
                    {
                        name: "week",
                        $el: this.$(".js-field-week")
                    },
                    {
                        name: "term",
                        $el: this.$(".js-field-term")
                    },
                    {
                        name: "day",
                        $el: this.$(".js-field-day")
                    },
                    {
                        name: "startHour",
                        $el: this.$(".js-field-start-hour")
                    },
                    {
                        name: "startMinute",
                        $el: this.$(".js-field-start-minute")
                    },
                    {
                        name: "endHour",
                        $el: this.$(".js-field-end-hour")
                    },
                    {
                        name: "endMinute",
                        $el: this.$(".js-field-end-minute")
                    }
                ];
            }

            return this.fields;
        },

        getJEditableFields: function () {
            // Return the fields which should have jeditable enabled
            return _.filter(this.getFields(), function (fieldData) {
                return fieldData.jeditable;
            });
        },

        syncModel: function () {
            // Push all field values into the model.
            this.model.set(this.getEventData());
        }
    });

    var EditableTitleView = Backbone.View.extend({
        initialize: function (options) {
            _.bindAll(this);
            //_.bindAll(this, "onToggleClick", "onClick", "saveAndClose");

            this.$toggleButton = options.$toggleButton;
            this.titleFieldName = options.titleFieldName || "title";

            this.$value = this.$(".js-value");

            this.model = new TitleModel({
                titleFieldName: options.titleFieldName
            });

            this.updateModel();
            this.model.storeInitialState();

            this.initJEditable();
            this.$toggleButton.on("click", this.onToggleClick);
        },

        events: {
            "click": "onClick",
            "keyup .js-value": "onValueKeyup"
        },

        onValueKeyup: function (event) {
            var $target = $(event.target);
            if ($target.is(".js-value") && event.keyCode === 13 && !$target.find("form").length) {
                $target.trigger("click");
            }
        },

        onClick: function (event) {
            // Stop this event from propagating to prevent the collapse
            // functionality to be triggered when the title is being edited.
            if (this.$value.find("input").length) {
                event.stopPropagation();
            }
        },

        startEdit: function () {
            this.$value.trigger("edit");
        },

        initJEditable: function () {
            var self = this;
            this.$value.editable(function (value) {
                self.$value.removeClass("being-edited");
                return value;
            }, {
                onblur: "submit",
                type: "title",
                event: "edit",
                callback: this.saveAndClose,
                maxLength: 512,
                select: true,
                onreset: function () {
                    // Revert the value to what's in the model
                    self.revert();
                    // Trigger a submit
                    $(this).find("input").blur();
                    self.focusToggleButton();
                    // Prevent the default jeditable reset
                    return false;
                }
            });
        },

        setSavePath: function (savePath) {
            this.$(".js-value").data("save-path", savePath);
        },

        setSavingState: function (saving) {
            this.$value.toggleClass("saving", saving);
        },

        setErrorState: function (error) {
            var $errorMessage = this.$(".js-error-message");
            $errorMessage.toggle(error !== false);
            $errorMessage.text(error || "");
        },

        lock: function () {
            this.locked = true;
        },

        onToggleClick: function (event) {
            event.preventDefault();
            if (this.isSaving || this.locked) {
                return;
            }

            this.startEdit();
        },

        updateModel: function () {
            this.model.set(this.titleFieldName, this.$value.text());
        },

        revert: function () {
            var $input = this.$value.find("input");
            if ($input.length) {
                $input.val(this.model.getInitialValue(this.titleFieldName));
                return;
            }

            this.$value.text(this.model.getInitialValue(this.titleFieldName));
        },

        focusToggleButton: function () {
            focusHelper.focusTo(this.$toggleButton);
        },

        saveAndClose: function () {
            this.setErrorState(false);
            this.updateModel();

            if (this.locked || !this.model.isValid()) {
                this.revert();
                this.trigger("cancel");
                this.focusToggleButton();
                return;
            }

            if (this.model.hasChangedFromOriginal()) {
                this.saveData();
            }
            this.focusToggleButton();
            return false;
        },

        getEncodedData: function () {
            var data = this.model.asJSONDjangoForm();
            // Add extra saveData object to data. This is needed for creating
            // new modules. Won't overwrite any properties already defined in
            // data.
            _.defaults(data, this.options.extraSaveData);
            return DjangoForms.encodeJSONForm(data);
        },

        saveData: function () {
            var self = this;
            this.setSavingState(true);

            $.ajax({
                type: "POST",
                url: this.$value.data("save-path"),
                data: this.getEncodedData(),
                success: function (data) {
                    self.setSavingState(false);
                    self.setErrorState(false);
                    self.$value.text(data[self.titleFieldName]);
                    self.updateModel();
                    self.model.storeInitialState(true);
                    self.trigger("save", data);
                    // Reapply focus
                    self.focusToggleButton();
                },
                error: function (error) {
                    var responseText = "Saving failed, please try again later.";

                    if (error.status === 500) {
                        self.revert();
                    } else {
                        responseText = error.responseText || responseText;
                    }

                    self.model.reset();
                    self.setSavingState(false);
                    self.setErrorState(responseText);
                    self.startEdit();
                }
            });
        }
    });

    var DateTimeDialogView = Backbone.View.extend({
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

        /**
         * Returns true if the popup window is located outside of the viewport.
         */
        outsideViewport: function () {
            var windowTop = $(window).scrollTop(),
                windowBottom = windowTop + $(window).height(),
                popupTop = this.$el.offset().top,
                popupBottom = popupTop + this.$el.height();

            return popupBottom > windowBottom || popupTop < windowTop;
        },

        /**
         * Shows the dialog and scrolls to its location if it's positioned
         * outside the viewport.
         */
        show: function () {
            var self = this;
            this.$el.show();

            if (this.outsideViewport()) {
                this.scrollTo(function () {
                    self.focus();
                });
            } else {
                this.focus();
            }
        },

        /**
         * Puts the window focus on the first input element.
         */
        focus: function () {
            focusHelper.focusTo(this.$("#date-time-week"));
        },

        /**
         * Scrolls the window to the location of the popup.
         */
        scrollTo: function (callback) {
            var scrollPosition = this.$el.offset().top - ($(window).height() / 2 - this.$el.height() / 2);
            $("html, body").stop().animate({
                "scrollTop": scrollPosition
            }, 400, callback);
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
            focusHelper.focusTo(this.$(".js-week"));
        },

        /** Focus the last form element. */
        focusEnd: function() {
            focusHelper.focusTo(this.$(".js-minute.js-end"));
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
        events: function() {
            return {
                "click .btn": this.dismissDialog
            };
        },

        initialize: function() {
            _.bindAll(this);

            this.setElement($("#templates .js-events-save-dialog").clone()[0]);
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

        postEventsForm: function(id, eventsData) {
            var self = this;
            this.$el.on("shown", function () {
                api.saveEvents(id, eventsData, function (error, response) {
                    if (error) {
                        self.onPOSTFail();
                        return;
                    }

                    self.onPOSTDone(response);
                });
            });
            this.showModal();
        },

        onPOSTDone: function(response) {
            this.$(".js-body").hide();
            this.$(".js-body-success").show();
            this.trigger("saved", response);
            focusHelper.focusTo(this.$(".btn-success"));
        },

        onPOSTFail: function() {
            this.$(".js-body").hide();
            this.$(".js-body-error").show();
            focusHelper.focusTo(this.$(".btn-danger"));
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
        initialize: function (opts) {
            TitleModel.__super__.initialize.apply(this, arguments);
            this.titleFieldName = opts.titleFieldName || "title";
        },

        /**
         * Returns true if the model has a valid value for the title.
         */
        isValid: function () {
            var cleanTitle = this.get(this.get("titleFieldName")).toLowerCase();
            return cleanTitle !== "" && cleanTitle !== "series title" && cleanTitle !== "module title";
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
        listEvents: listEvents,
        BaseModel: BaseModel
    };
});

