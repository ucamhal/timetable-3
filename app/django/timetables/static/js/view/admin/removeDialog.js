define([
    "jquery",
    "underscore",
    "backbone",
    "bootstrap"
], function ($, _, Backbone) {
    "use strict";

    /**
     * ============
     * RemoveDialog
     * ============
     *
     * Class for a popup repsonsible for removing important things!
     * Expects ".js-remove-popup" to be available in the DOM.
     * _________________________________________________________________________
     * 
     * Has 4 possible states:
     * - Start: Shows we're going to remove something, user has to confirm
     * deletion.
     * - Progress: Shows a progress bar comminicating that we're in the progress
     * of removing what the user wanted to remove. Dialog can't be closed in
     * this state.
     * - Success: The removal has been successfully completed. Shows a
     * confirmation message to the user.
     * - Error: Something has gone wrong, shows an error message to the user.
     * _________________________________________________________________________
     *
     * Needs three provided options to work:
     * - Type: The type of the object being removed (e.g. series, module, etc)
     * - Title: The title of the object that's being removed
     * - Contents: A string explaining to the user what the contents of the item
     * that's being removed are.
     */

    var RemoveDialog = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this);

            this.$el = $(".js-delete-popup").clone();
            this.model = new Backbone.Model({
                title: this.options.title,
                type: this.options.type,
                contents: this.options.contents,
                state: "start"
            });

            this.bindEvents();
            this.render();

            this.$el.modal({
                backdrop: "static",
                keyboard: false,
                show: true
            });
        },

        /**
         * Bind all necessary external events.
         */
        bindEvents: function () {
            this.model.on("change:type", this.renderType);
            this.model.on("change:title", this.renderTitle);
            this.model.on("change:contents", this.renderContents);
            this.model.on("change:state", this.renderState);
        },

        events: {
            "click .js-confirm": "onClickConfirm",
            "hidden": "onHide"
        },

        onClickConfirm: function (event) {
            // Change the state to progress
            this.setState("progress");
            this.trigger("confirm");
            event.preventDefault();
        },

        onHide: function () {
            this.trigger("close");
        },

        onError: function () {
            this.setState("error");
        },

        onSuccess: function () {
            this.$el.modal("hide");
        },

        /**
         * Set the type in the model to the supplied value.
         */
        setType: function (type) {
            this.model.set("type", type);
        },

        /**
         * Set the title in the model to the supplied value.
         */
        setTitle: function (title) {
            this.model.set("title", title);
        },

        /**
         * Set the result in the model to the supplied value.
         */
        setContents: function (contents) {
            this.model.set("contents", contents);
        },

        /**
         * Set the state in the model to the supplied value.
         */
        setState: function (state) {
            this.model.set("state", state);
        },

        /**
         * Updates everything in the DOM to the model's state.
         */
        render: function () {
            this.renderType();
            this.renderTitle();
            this.renderContents();
            this.renderState();
        },

        /**
         * Renders the type to what is present as the type in the model.
         */
        renderType: function () {
            this.$(".js-delete-type").text(this.model.get("type"));
        },

        /**
         * Renders the title to what is present as the title in the model.
         */
        renderTitle: function () {
            this.$(".js-delete-title").text(this.model.get("title"));
        },

        /**
         * Renders the result text to what is present as the result in the
         * model.
         */
        renderContents: function () {
            this.$(".js-delete-contents").text(this.model.get("contents"));
        },

        /**
         * Renders the popup state to what is present as the state in the model.
         */
        renderState: function () {
            var state = this.model.get("state");
            this.$(".modal-body, .modal-footer").hide();
            this.$(".modal-header .close").toggle(state !== "progress");
            this.$(".js-state-" + state).show();
        }
    });

    return RemoveDialog;
});
