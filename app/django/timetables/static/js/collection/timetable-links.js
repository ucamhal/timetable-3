define([
    "underscore",
    "backbone",
    "model/timetable-link"
], function (_, Backbone, TimetableLinkModel) {
    "use strict";

    var TimetableLinkCollection = Backbone.Collection.extend({
        model: TimetableLinkModel,

        getLinkFullpaths: function () {
            return this.pluck("linkFullpath");
        }
    });

    return TimetableLinkCollection;
});
