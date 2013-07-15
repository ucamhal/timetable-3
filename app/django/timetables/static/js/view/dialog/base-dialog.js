define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {
    "use strict";

    var BaseDialog = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this);
            this.$el.addClass("modal fade").modal({
                backdrop: "static",
                keyboard: false,
                show: true
            });
        },

        tagName: "div",

        events: function () {
            return {
                "hidden": this.onHide
            };
        },

        onHide: function () {
            this.off();
            this.remove();
            this.trigger("close");
        },

        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
        }
    });

    return BaseDialog;
});
