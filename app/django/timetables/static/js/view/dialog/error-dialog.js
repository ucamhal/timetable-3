define([
    "jquery",
    "underscore",
    "backbone",
    "view/dialog/base-dialog"
], function ($, _, Backbone, BaseDialog) {
    "use strict";

    var ErrorDialog = BaseDialog.extend({
        initialize: function () {
            // Apply initialization of superclass
            ErrorDialog.__super__.initialize.apply(this, arguments);

            this.model = new Backbone.Model({
                titleText: this.options.titleText || "Woops, something went wrong...",
                messageText: this.options.messageText || "Please try again later.",
                closeable: this.options.closeable !== undefined ? this.options.closeable : true,
                customFooterContent: this.options.customFooterContent
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
