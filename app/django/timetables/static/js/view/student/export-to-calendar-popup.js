define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {
    "use strict";

    var ExportToCalendarPopup = Backbone.View.extend({
        initialize: function (opts) {
            _.bindAll(this);
            this.model = new Backbone.Model({
                resetUrl: opts.resetUrl
            });
            this.bindEvents();
        },

        events: {
            "click .js-reset-feed": "onResetFeedClick",
            "hide": "onHide"
        },

        bindEvents: function () {
            this.listenTo(this.model, "change:state", this.onStateChange);
        },

        constructGoogleFeedUrl: function (feedUrl) {
            return "https://www.google.com/calendar/render?cid=" + escape(feedUrl);
        },

        updateFeed: function (feedUrl) {
            this.$(".js-feed-container p").text(feedUrl);
            this.$(".js-btn-google-calendar").attr("href", this.constructGoogleFeedUrl(feedUrl));
        },

        onResetFeedClick: function () {
            var self = this;
            this.setState("busy");

            $.ajax({
                type: "post",
                url: this.model.get("resetUrl"),
                success: function (data) {
                    self.updateFeed(data);
                    self.setState();
                },
                error: function () {
                    self.setState("error");
                }
            });
        },

        onHide: function () {
            // Prevent hiding the popup if the application is busy resetting the
            // feed url.
            if (this.model.get("state") === "busy") {
                return false;
            }
        },

        setState: function (state) {
            this.model.set("state", state);
        },

        onStateChange: function (model, state) {
            var previousState = model.previous("state");
            if (previousState) {
                this.$el.removeClass(previousState);
            }
            this.$el.addClass(state);
        }
    });

    return ExportToCalendarPopup;

});
