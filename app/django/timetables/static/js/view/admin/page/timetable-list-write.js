define([
    "jquery",
    "underscore",
    "backbone",
    "view/admin/lists",
    "view/admin/timetable-links",
    "util/focus-helper",
    "bootstrap"
], function($, _, Backbone, Lists, TimetableLinks, focusHelper) {
    "use strict";

    var TimetableListWrite = Backbone.View.extend({
        initialize: function () {
            var modules = [],
                self = this;

            _.bindAll(this);

            $(".js-module").each(function() {
                var moduleView = new Lists.WritableModuleView({
                    el: this
                });
                moduleView.on("remove", self.removeModule);
                modules.push(moduleView);
            });

            this.model = new Lists.BaseModel();
            this.listenTo(this.model, "change", this.onModelChange);
            this.model.set({
                moduleViews: modules,
                newModuleViews: []
            });

            this.initTimetableLinks();
        },

        onModelChange: function () {
            var modules = this.model.get("moduleViews"),
                newModules = this.model.get("newModuleViews"),
                hasModules = (modules.length || newModules.length);

            this.$(".js-no-modules-msg").toggle(!hasModules);
        },

        initTimetableLinks: function () {
            var links = $(".js-links-list").data("links");

            this.timetableLinks = new TimetableLinks({
                el: ".js-linked-timetables",
                timetableFullpath: this.getTimetableFullpath()
            });

            _.each(_.map(links, function (link) {
                return link.fullpath;
            }), this.timetableLinks.addLink);
        },

        events: function () {
            return {
                "click .js-btn-add-module": this.onAddModuleClick
            };
        },

        getTimetableId: function () {
            return this.$el.data("id");
        },

        getTimetableFullpath: function () {
            return this.$el.data("fullpath");
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
                added: true,
                extraSaveData: {
                    "id_parent": this.getTimetableId()
                }
            });

            newModuleView.on("remove", this.removeModule);
            this.model.set({
                newModuleViews: this.model.get("newModuleViews").concat(newModuleView)
            });
        },

        removeModule: function (removedModule) {
            var target = removedModule.options.added === true ? "newModuleViews" : "moduleViews",
                $focusTarget = removedModule.$el.prev().find(".js-edit-icon");
            this.model.set(target, _.without(this.model.get(target), removedModule));

            if (!$focusTarget.length) {
                $focusTarget = this.$(".js-btn-add-module");
            }

            removedModule.destroy();
            // handle the focus
            focusHelper.focusTo($focusTarget);
        },

        onAddModuleClick: function (event) {
            var prepend = $(event.currentTarget).hasClass("js-prepend");
            this.appendNewModule(prepend);
            event.preventDefault();
        }
    });

    var timetablesListWrite = new TimetableListWrite({
        el: ".js-timetable"
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
        fullpath: $(".js-timetable").data("fullpath"),
        onTimeout: function () {
            // Lock all moduleviews including the new ones.
            _.invoke(timetablesListWrite.moduleViews, "lock");
            _.invoke(timetablesListWrite.newModuleViews, "lock");
        }
    });

    // Fire an initial hashchange to handle hash params in the URL on
    // page load.
    $(window).trigger("hashchange");

    // Not implemented yet:
    /*
    $(window).bind("beforeunload", function () {
        locker.unlock();
    });
    */

    Lists.listEvents.on("page-edited", locker.preventTimeout);

    return undefined;
});
