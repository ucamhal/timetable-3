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
            var modules = [];

            _.bindAll(this);

            $(".js-module").each(function() {
                modules.push(new Lists.WritableModuleView({el: this}));
            });

            this.model = new Lists.BaseModel();
            this.model.on("change", this.onModelChange);
            this.model.set({
                moduleViews: modules,
                newModuleViews: []
            });
        },

        // Only show the last add modules button if there are modules on the
        // page.
        onModelChange: function () {
            // There is always at least 1 moduleView: the general lectures one.
            var hasModules = this.model.get("moduleViews").length > 1 || this.model.get("newModuleViews").length > 0;
            this.$(".js-btn-add-module").last().toggle(hasModules);
        },

        events: function () {
            return {
                "click .js-btn-add-module": this.onAddModuleClick
            };
        },

        appendNewModule: function (prepend) {
            var $markup = $($("#js-templ-new-module").html()),
                $addTo = this.$(".js-individual-modules"),
                newModuleView;

            if (prepend === true) {
                $addTo.prepend($markup);
            } else {
                $addTo.append($markup);
            }

            newModuleView = new Lists.WritableModuleView({
                el: $markup,
                added: true
            });

            newModuleView.on("destroy", this.removeModule);
            newModuleView.editableTitle.toggleEditableState(true);
            this.model.set({
                newModuleViews: this.model.get("newModuleViews").concat(newModuleView)
            });
        },

        removeModule: function (removedModule) {
            var target = removedModule.options.added === true ? "newModuleViews" : "moduleViews";
            this.model.set(target, _.without(this.model.get(target), removedModule));
        },

        onAddModuleClick: function (event) {
            var prepend = $(event.currentTarget).hasClass("js-prepend");
            this.appendNewModule(prepend);
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
