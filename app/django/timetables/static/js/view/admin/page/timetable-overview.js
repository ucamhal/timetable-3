define([
    "jquery",
    "underscore",
    "backbone",
    "util/api-admin",
    "bootstrap"
], function ($, _, Backbone, api) {
    "use strict";

    // The number of milliseconds between timetable status updates.
    var UPDATE_FREQUENCY = 1000 * 10;

    $("select.js-select-faculty").change(function() {
        var target = $(this).val();
        $(window.location).attr("href", "/" + target + ".home.admin.html");
    });

    var EditableTimetable = Backbone.View.extend({
        initialize: function () {
            this.$editMessage = this.$(".js-edit-message");
            this.$name = this.$(".js-editor");
        },

        setBeingEdited: function (isBeingEdited, by) {
            this.$name.text(by);
            this.$editMessage.toggle(isBeingEdited);
            this.$el.toggleClass("being-edited", isBeingEdited);
        },

        getFullpath: function() {
            return this.$el.data("fullpath");
        }
    });

    var timetables = _.map($(".js-timetable-editable"), function (el) {
        return new EditableTimetable({el: el});
    });

    var editableTimetables = $.param(_.map(timetables, function(tt){
        return {name: "timetables[]", value: tt.getFullpath()};
    }));

    // Create an object mapping timetable fullpaths to the timetable
    var timetablePaths = _.object(_.map(timetables, function(tt) {
        return [tt.getFullpath(), tt];
    }));

    function updateTimetablesLockStatus () {
        api.getTimetablesLockStatuses(editableTimetables, function (error, statuses) {
            if (error) {
                console.log("timetables update lock status failure");
                return;
            }

            _.each(statuses, function(status, fullpath) {
                var timetable = timetablePaths[fullpath];
                var editor = status.name;

                if (timetable) {
                    timetable.setBeingEdited(Boolean(editor), editor);
                }
            });
        });
    }

    // Update the lock status straight away
    updateTimetablesLockStatus();
    setInterval(updateTimetablesLockStatus, UPDATE_FREQUENCY);
});
