define([
    "underscore",
    "backbone"
], function (_, Backbone) {
    "use strict";

    // Backbone.Events contains basic event listening/triggering behaviour
    return _.extend({}, Backbone.Events);
});
