define([
    "underscore",
    "backbone",
    "util/admin-api"
], function (_, Backbone, api) {
    "use strict";

    var TimetableLinkModel = Backbone.Model.extend({
        defaults: {
            timetableFullpath: "",
            linkFullpath: "",
            moduleName: "",
            partName: "",
            disabled: []
        },

        // Overwrite default backbone save behavior
        save: function (callback) {
            api.addThingLink(this.get("timetableFullpath"), this.get("linkFullpath"), callback);
        },

        remove: function (callback) {
            api.removeThingLink(this.get("timetableFullpath"), this.get("linkFullpath"), callback);
        },

        /**
         * Overwrite the destroy method to only dispatch an event.
         */
        destroy: function (options) {
            this.trigger("destroy", this, this.collection, options);
        }
    });

    return TimetableLinkModel;
});
