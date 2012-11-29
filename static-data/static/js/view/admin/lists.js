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
				"show .js-module-content": "onExpand",
				"hide .js-module-content": "onCollapse",
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
		}
	});
	
	var SeriesView = Backbone.View.extend({
		constructor: function SeriesView() {
			SeriesView.__super__.constructor.apply(this, arguments);
		},

		events: function() {
			return {
				"show .js-events": "onExpand",
				"hide .js-events": "onCollapse",
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

		startEventsRequest: function() {
			this.loadingIndicator.showLoadingState();

			// make the ajax request to fetch the events
			$.ajax("/series/" + encodeURIComponent(this.getSeriesId()) 
				+ "/list-events", {})
				.done(this.onEventsFetched)
				.fail(this.onEventsFetchFailed);
		},

		onEventsFetched: function(response) {
			console.log("got events", arguments);
			
			delete this.loadingIndicator;
			this.$(".js-events").empty().append(response);
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

	return {
		ModuleView: ModuleView,
		SeriesView: SeriesView
	};
});