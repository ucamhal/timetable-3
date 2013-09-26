define([
    "jquery",
    "underscore",
    "view/dialog/error-dialog",
    "util/timetable-events"
], function ($, _, ErrorDialog, timetableEvents) {
    "use strict";

    var ErrorNotSignedInDialog = ErrorDialog.extend({
        events: function () {
            var parentEvents = ErrorNotSignedInDialog.__super__.events.apply(this, arguments);
            return _.extend(parentEvents, {
                "click .js-sign-in": this.onSignInClick
            });
        },

        onSignInClick: function () {
            timetableEvents.trigger("click_signin");
        }
    });

    return ErrorNotSignedInDialog;
});
