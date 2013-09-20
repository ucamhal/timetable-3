define([
    "jquery",
    "underscore",
    "backbone",
    "view/dialog/base-dialog",
    "util/focus-helper",
    "util/api-student",
    "util/timetable-events",
    "util/jquery.select-text"
], function ($, _, Backbone, BaseDialog, focusHelper, api, timetableEvents) {
    "use strict";

    var ExportToCalendarDialog = BaseDialog.extend({
        initialize: function (options) {
            ExportToCalendarDialog.__super__.initialize.apply(this, arguments);

            this.model = new Backbone.Model({
                userPath: options.userPath || "",
                feedPath: options.feedPath || "",
                state: options.state || "idle"
            });

            this.bindEvents();
            this.render();
        },

        template: _.template($("#js-templ-export-to-calendar-dialog").html()),

        events: function () {
            var superEvents = ExportToCalendarDialog.__super__.events.call(this);
            return _.extend(superEvents, {
                "focus .js-feed-container": this.onFeedContainerFocus,
                "click .js-feed-container": this.onFeedContainerClick,
                "click .js-reset-feed": this.onResetFeedClick,
                "hide": this.onHide
            });
        },

        onResetFeedClick: function() {
            var self = this,
                userPath = this.model.get("userPath");

            if (this.model.get("state") === "busy") {
                return;
            }

            this.model.set("state", "busy");
            timetableEvents.trigger("click_btn_feed_reset");

            api.resetUserFeed(userPath, function(error, response) {
                if (error) {
                    self.model.set("state", "error");
                    return;
                }

                self.model.set({
                    feedPath: response,
                    state: "idle"
                });
                self.trigger("feedChanged", response);
                focusHelper.focusTo(self.$(".js-feed-container"));
            });
        },

        onHide: function () {
            // Prevent hiding the popup if the application is busy resetting the
            // feed url.
            if (this.model.get("state") === "busy") {
                return false;
            }
        },

        onShown: function () {
            focusHelper.focusTo(this.$(".js-feed-container"));
        },

        bindEvents: function () {
            this.listenTo(this.model, "change", this.render);
        },

        selectFeedPath: function () {
            if (!focusHelper.isIE()) {
                var self = this;
                // Wait until all focus behavior has finished
                _.defer(function () {
                    // Select the feed url
                    self.$(".js-feed-container p").selectText();
                });
            }
        },

        onFeedContainerFocus: function () {
            this.selectFeedPath();
        },

        onFeedContainerClick: function () {
            timetableEvents.trigger("click_feed_path");
        },

        render: function () {
            ExportToCalendarDialog.__super__.render.apply(this, arguments);
            this.$el.removeClass("idle busy error");
            this.$el.addClass("modal-export-to-calendar").addClass(this.model.get("state"));
        }
    });

    return ExportToCalendarDialog;

});
