define([
    "jquery",
    "underscore",
    "backbone",
    "view/admin/lists",
    "view/cookieHandler",
    "bootstrap",
    "not-implemented-tooltips"
], function($, _, Backbone, Lists, CookieHandler) {
    "use strict";

    var TimetableListWrite = Backbone.View.extend({
        initialize: function () {
            var self = this;

            $(".js-module").each(function() {
                self.moduleViews.push(new Lists.WritableModuleView({el: this}));
            });

            _.bindAll(this);
        },

        // Arrays to store the modules and series views in
        moduleViews: [],
        // and any newly added ones
        newModuleViews: [],

        events: function () {
            return {
                "click .js-btn-add-module": this.onAddModuleClick
            };
        },

        appendNewModule: function () {
            var $markup = $($("#js-templ-new-module").html()),
                newModuleView;

            this.$(".modulesList").append($markup);
            newModuleView = new Lists.WritableModuleView({
                el: $markup,
                added: true
            });

            newModuleView.on("destroy", this.removeModule);
            newModuleView.editableTitle.toggleEditableState(true);
            this.newModuleViews.push(newModuleView);
        },

        removeModule: function (removedModule) {
            var target = removedModule.options.added === true ? "newModuleViews" : "moduleViews";
            this[target] = _.without(this[target], removedModule);
        },

        onAddModuleClick: function (event) {
            this.appendNewModule();
            event.preventDefault();
        }
    });

    var timetablesListWrite = new TimetableListWrite({
        el: "body"
    });

    // Make the list watch for URL hash items in order to expand series
    // & highlight events.
    Lists.bindUrlHashWatcher();

    var locker = new Lists.Locker({
        // Minimum time between edit lock refreshes
        preventTimeoutTime: 1000 * 60 * 2,
        // Time between short term lock refreshes
        pingTime: 1000 * 10,
        $timedOutModal: $(".js-timedout-modal"),
        refreshUrl: $(".js-module-list").data("lock-refresh-path"),
        onTimeout: function () {
            // Lock all moduleviews including the new ones.
            _.invoke(timetablesListWrite.moduleViews, "lock");
            _.invoke(timetablesListWrite.newModuleViews, "lock");
        }
    });

    // Fire an initial hashchange to handle hash params in the URL on
    // page load.
    $(window).trigger("hashchange");
    $(window).bind("beforeunload", function () {
        locker.unlock();
    });

    Lists.listEvents.on("page-edited", locker.preventTimeout);

    new CookieHandler({
        el: ".js-cookie-alert"
    });

    return undefined;
});
