define([
    "jquery",
    "underscore",
    "backbone",
    "util/student-api",
    "util/jquery.select-text"
], function ($, _, Backbone, api) {
    "use strict";

    var ExportToCalendarPopup = Backbone.View.extend({
        initialize: function (opts) {
            _.bindAll(this);
            this.model = new Backbone.Model({
                userPath: opts.userPath
            });
            this.bindEvents();
        },

        events: {
            "click .js-reset-feed": "onResetFeedClick",
            "click .js-feed-container": "onFeedContainerClick",
            "hide": "onHide"
        },

        bindEvents: function () {
            this.listenTo(this.model, "change:state", this.onStateChange);
        },

        updateFeed: function (feedUrl) {
            this.$(".js-feed-container p").text(feedUrl);
        },

        onFeedContainerClick: function (event) {
            // Currently disabled this in IE because there is a bootstrap issue
            // which prevents the text from being properly selected.
            if (!$.browser.msie) {
                this.$(".js-feed-container p").selectText();
            }
            event.preventDefault();
        },

        onResetFeedClick: function () {
            var self = this,
                userPath = this.model.get("userPath");

            this.setState("busy");

            api.resetUserFeed(userPath, function (error, response) {
                if (error) {
                    self.setState("error");
                    return;
                }

                self.updateFeed(response);
                self.setState();
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
