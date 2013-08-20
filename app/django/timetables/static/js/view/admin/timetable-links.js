define([
    "jquery",
    "underscore",
    "backbone",
    "collection/timetable-links",
    "view/admin/timetable-link",
    "util/dialog-factory-admin"
], function ($, _, Backbone, TimetableLinksCollection, TimetableLinkView, dialogFactory) {
    "use strict";

    var TimetableLinks = Backbone.View.extend({
        initialize: function (opts) {
            this.collection = opts.collection || new TimetableLinksCollection();
            this.$linksList = this.$(".js-links-list");

            _.bindAll(this);
            this.bindEvents();
            this.render();
        },

        bindEvents: function () {
            this.listenTo(this.collection, "add", this.addOne);
        },

        events: {
            "click .js-btn-add-link": "onAddLinkClick"
        },

        addOne: function (model) {
            var timetableLinkView = new TimetableLinkView({
                model: model
            });
            timetableLinkView.render();

            if (!model.get("linkFullpath")) {
                timetableLinkView.toggleEditState();
            } else {
                timetableLinkView.updateModel();
                this.addDisabledFullpath(model.get("linkFullpath"));
            }

            this.listenTo(timetableLinkView, "save", this.onLinkViewSave);
            this.listenTo(timetableLinkView, "remove", this.onLinkViewRemove);
            this.$linksList.append(timetableLinkView.el);
        },

        onLinkViewSave: function (linkView) {
            var fullpath = linkView.model.get("linkFullpath"),
                self = this;

            if (!fullpath) {
                dialogFactory.saveLinkSelectError();
                return;
            }

            if (fullpath === this.options.timetableFullpath) {
                dialogFactory.saveLinkTimetableError();
                return;
            }

            if (_.contains(this.disabledFullpaths, fullpath)) {
                dialogFactory.saveLinkClashError();
                return;
            }

            linkView.model.save(function (error) {
                if (error) {
                    dialogFactory.saveLinkError({
                        link: fullpath
                    });
                    return;
                }
                linkView.toggleEditState();
                self.addDisabledFullpath(fullpath);
            });
        },

        onLinkViewRemove: function (linkView) {
            var self = this,
                moduleName = linkView.model.get("moduleName"),
                partName = linkView.model.get("partName"),
                fullpath = linkView.model.get("linkFullpath"),
                removeDialog = new dialogFactory.removeLink({
                    link: moduleName + ", " + partName,
                    timetable: $(".js-timetable-title").text()
                });

            this.listenTo(removeDialog, "confirm", function () {
                linkView.model.remove(function (error) {
                    if (error) {
                        removeDialog.onError();
                        return;
                    }

                    removeDialog.onSuccess();
                    linkView.model.destroy();
                    self.removeDisabledFullpath(fullpath);
                });
            });
        },

        addDisabledFullpath: function (fullpath) {
            this.disabledFullpaths = this.disabledFullpaths || [];
            this.disabledFullpaths.push(fullpath);
        },

        removeDisabledFullpath: function (fullpath) {
            this.disabledFullpaths = _.without(this.disabledFullpaths, fullpath);
        },

        addAll: function () {
            this.collection.each(this.addOne);
        },

        addLink: function (linkFullpath) {
            this.collection.add({
                timetableFullpath: this.options.timetableFullpath,
                linkFullpath: linkFullpath
            });
        },

        onAddLinkClick: function () {
            this.addLink();
        },

        render: function () {
            this.$linksList.html();
            this.addAll();
        }
    });

    return TimetableLinks;
});
