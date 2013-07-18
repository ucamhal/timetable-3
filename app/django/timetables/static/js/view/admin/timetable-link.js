define([
    "jquery",
    "underscore",
    "backbone",
    "view/modules-selector"
], function ($, _, Backbone, ModulesSelector) {
    "use strict";

    var TimetableLinkView = Backbone.View.extend({
        template: _.template($.trim($("#js-templ-link").html())),
        tagName: "li",

        initialize: function () {
            _.bindAll(this);
            this.bindEvents();
        },

        bindEvents: function () {
            this.listenTo(this.model, "destroy", this.onDestroy);
            this.listenTo(this.model, "change", this.render);
        },

        events: {
            "click .js-btn-save": "onSaveClick",
            "click .js-btn-cancel": "onCancelClick",
            "click .js-btn-remove": "onRemoveClick"
        },

        onSaveClick: function () {
            this.updateModel();
            this.trigger("save", this);
        },

        onRemoveClick: function () {
            this.trigger("remove", this);
        },

        onCancelClick: function () {
            this.model.destroy();
        },

        onDestroy: function () {
            this.modulesSelector.remove();
            this.remove();
        },

        updateModel: function () {
            var linkFullpath = this.modulesSelector.getValue();
            this.model.set({
                linkFullpath: linkFullpath,
                partName: this.modulesSelector.getPartTextFromFullpath(linkFullpath),
                moduleName: this.modulesSelector.getModuleTextFromFullpath(linkFullpath)
            });
        },

        toggleEditState: function () {
            this.$el.toggleClass("edit");
        },

        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            this.initModulesSelector();
            this.updateModulesSelector();
        },

        updateModulesSelector: function () {
            this.modulesSelector.setSelectsFromFullpath(this.model.get("linkFullpath"));
        },

        initModulesSelector: function () {
            this.modulesSelector = new ModulesSelector({
                el: this.$(".js-selector")[0]
            });
        }
    });

    return TimetableLinkView;
});
