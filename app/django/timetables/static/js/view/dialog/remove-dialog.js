define([
    "jquery",
    "underscore",
    "backbone",
    "view/dialog/base-dialog",
    "bootstrap"
], function ($, _, Backbone, BaseDialog) {
    "use strict";

    var RemoveDialog = BaseDialog.extend({
        constructor: function RemoveDialog () {
            RemoveDialog.__super__.constructor.apply(this, arguments);
        },

        initialize: function () {
            // Apply initialization of superclass
            RemoveDialog.__super__.initialize.apply(this, arguments);

            this.model = new Backbone.Model({
                titleText: this.options.titleText,
                contentsText: this.options.contentsText,
                confirmBtnText: this.options.confirmBtnText,
                removingTitleText: this.options.removingTitleText,
                errorText: this.options.errorText,
                state: "start"
            });

            this.bindEvents();
            this.render();
        },

        template: _.template($("#js-templ-remove-dialog").html()),

        /**
         * Bind all necessary external events.
         */
        bindEvents: function () {
            this.model.on("change", this.render);
        },

        events: function () {
            var superEvents = RemoveDialog.__super__.events.call(this);
            return _.extend(superEvents, {
                "click .js-confirm": this.onClickConfirm
            });
        },

        onClickConfirm: function (event) {
            // Change the state to progress
            this.setState("progress");
            this.trigger("confirm");
            event.preventDefault();
        },

        onError: function () {
            this.setState("error");
        },

        onSuccess: function () {
            this.$el.modal("hide");
        },

        /**
         * Set the state in the model to the supplied value.
         */
        setState: function (state) {
            this.model.set("state", state);
        }
    });

    return RemoveDialog;
});
