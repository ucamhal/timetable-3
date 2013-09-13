define([
    "underscore",
    "backbone",
    "util/api",
    "util/dialog-factory"
], function (_, Backbone, api, dialogFactory) {
    "use strict";

    var CalendarEventPopupModel = Backbone.Model.extend({
        initialize: function () {
            _.bindAll(this);
        },

        defaults: {
            id: undefined,
            title: "",
            datePattern: "",
            location: "",
            lecturers: "",
            type: "",
            seriesId: undefined,
            subjectTitle: "",
            state: "idle"
        },

        updateSubjectTitle: function (callback) {
            var self = this;
            this.set("state", "busy");
            api.getSeriesSubject(this.get("seriesId"), function (error, response) {
                self.set("state", "idle");
                if (error) {
                    dialogFactory.unknownError();
                    self.set("subjectTitle", undefined);
                    return;
                }
                // Only update the subject and call the callback if the series
                // id from the response corresponds with the id set in the model
                if (Number(response.series_id) === self.get("seriesId")) {
                    self.set("subjectTitle", response.subject);
                    if (_.isFunction(callback)) {
                        callback();
                    }
                }
            });
        }
    });

    return CalendarEventPopupModel;
});
