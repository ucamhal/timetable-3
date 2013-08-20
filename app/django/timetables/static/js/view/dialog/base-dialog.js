define([
    "jquery",
    "underscore",
    "backbone",
    "util/focus-helper",
    "bootstrap"
], function ($, _, Backbone, focusHelper) {
    "use strict";

    var BaseDialog = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this);
        },

        show: function () {
            this.$el.addClass("modal fade").modal({
                backdrop: "static",
                keyboard: false,
                show: true
            });
            return this;
        },

        tagName: "div",

        events: function () {
            return {
                "hidden": this.onHidden,
                "shown": this.onShown
            };
        },

        onShown: function () {
            focusHelper.focusTo(this.$(".btn").first());
        },

        onHidden: function () {
            this.trigger("close");
            this.off();
            this.remove();
        },

        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
        }
    });

    return BaseDialog;
});
