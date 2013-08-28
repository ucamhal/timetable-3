define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {
    "use strict";

    var DateSpinner = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this);

            this.model = new Backbone.Model({
                next: true,
                prev: true,
                value: undefined
            });

            this.$label = this.$(".js-value");
            this.bindEvents();
        },

        set: function (data) {
            this.model.set(data);
        },

        bindEvents: function () {
            this.listenTo(this.model, "change", this.render);
        },

        render: function () {
            this.updateLabel();
            this.updateButtons();
        },

        updateLabel: function () {
            this.$label.text(this.model.get("value"));
        },

        updateButtons: function () {
            this.$(".js-prev").toggleClass("disabled", !this.model.get("prev"));
            this.$(".js-next").toggleClass("disabled", !this.model.get("next"));
        },

        events: {
            "click .js-prev": "onClickPrevious",
            "click .js-next": "onClickNext"
        },

        onClickPrevious: function (event) {
            if (this.model.get("prev")) {
                this.trigger("prev");
            }
            event.preventDefault();
        },

        onClickNext: function (event) {
            if (this.model.get("next")) {
                this.trigger("next");
            }
            event.preventDefault();
        }
    });

    return DateSpinner;
});
