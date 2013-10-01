define([
    "underscore",
    "backbone",
    "util/timetable-events",
    "util/google-analytics",
    "util/page"
], function (_, Backbone, timetableEvents, ga, page) {
    "use strict";

    /**
     * List of categories and events that we want to report to GA
     * Keep these short as they are collapsed in Event Flow View (User Authentication -> U...entication etc.)
     */
    var categories = {
        auth: "Auth",
        cal_manip: "Edit",
        cal_export: "Export",
        cal_print: "Print",
        cal_view: "View"
    };

    /**
     * These are used as the identifiers of the actions in GA, but they're
     * also displayed in the reports. Ideally they should be short but
     * human-readable. Renaming these will effectively make a new event in
     * Google Analytics.
     *
     *     code reference                  ga category                     ga action          ga label
     */
    var events = {
        click_tab_agendaWeek:    {category: categories.cal_view,     action: "Switch View", label: "Week"},
        click_tab_month:         {category: categories.cal_view,     action: "Switch View", label: "Month"},
        click_tab_list:          {category: categories.cal_view,     action: "Switch View", label: "List"},
        interact_needs_login:    {category: categories.auth,         action: "Needs login"},
        click_signin:            {category: categories.auth,         action: "Click sign in"},
        click_signout:           {category: categories.auth,         action: "Click sign out"},
        click_add:               {category: categories.cal_manip,    action: "Click add"},
        click_remove:            {category: categories.cal_manip,    action: "Click remove"},
        click_btn_export:        {category: categories.cal_export,   action: "Click export"},
        on_before_print:         {category: categories.cal_print,    action: "Print"},
        click_btn_print:         {category: categories.cal_print,    action: "Click print"},
        click_feed_path:         {category: categories.cal_export,   action: "Click feed"},
        click_btn_feed_reset:    {category: categories.cal_export,   action: "Reset feed"},
        click_event:             {category: categories.cal_view,     action: "Click Event"}
    };

    var AnalyticsHandler = function () {
        this.initialize();
    };

    _.extend(AnalyticsHandler.prototype, {
        events: events,

        initialize: function () {
            _.bindAll(this);
            var GAID = page.getGoogleAnalyticsID();

            if (GAID) {
                // Initialize page tracking
                ga("create", page.getGoogleAnalyticsID());
                ga("set", {
                    "dimension1": page.getUserRole(),
                    "dimension2": page.getUserTripos()
                });
                ga("send", "pageview");

                this.bindEvents();
            }
        },

        bindEvents: function () {
            // Listens to all events and passes them through to "this.report".
            timetableEvents.on("all", this.report);
        },

        report: function (event, data) {
            // part_change is treated as a pageview.
            if (event === "part_change") {
                this.reportPageView(data);
            } else if (_.has(this.events, event)) {
                this.reportEvent(event);
            }
        },

        /**
         * Send a GA event report, passing a string identifying the event. The
         * string after the currently active fullpath will be passed as the
         * currently active page.
         */
        reportEvent: function (event) {
            var event_details = this.events[event],
                page = Backbone.history.getFragment();
            ga("send", "event", event_details.category, event_details.action, event_details.label, {
                page: page
            });
        },

        reportPageView: function (path) {
            ga("send", "pageview", path || Backbone.history.getFragment());
        }
    });

    return new AnalyticsHandler();
});
