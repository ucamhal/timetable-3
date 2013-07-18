define([
    "jquery",
    "underscore",
    "backbone",
    "view/dialog/base-dialog"
], function ($, _, Backbone, BaseDialog) {
    "use strict";

    var ErrorDialog = BaseDialog.extend({
        constructor: function ErrorDialog () {
            ErrorDialog.__super__.constructor.apply(this, arguments);
        },

        initialize: function () {
            // Apply initialization of superclass
            ErrorDialog.__super__.initialize.apply(this, arguments);

            this.model = new Backbone.Model({
                titleText: this.options.titleText || "Woops, something went wrong...",
                messageText: this.options.messageText || "Please try again later."
            });

            this.bindEvents();
            this.render();
        },

        template: _.template($("#js-templ-error-dialog").html()),

        bindEvents: function () {
            this.listenTo(this.model, "change", this.render);
        }
    });

    return ErrorDialog;
});
