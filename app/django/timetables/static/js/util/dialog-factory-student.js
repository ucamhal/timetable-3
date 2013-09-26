define([
    "jquery",
    "underscore",
    "view/dialog/error-dialog",
    "view/dialog/error-not-signed-in-dialog",
    "view/dialog/export-to-calendar-dialog",
    "util/dialog-factory"
], function ($, _, ErrorDialog, ErrorNotSignedInDialog, ExportToCalendarDialog, dialogFactory) {
    "use strict";

    var notSignedInError = function notSignedInError(data) {
        return new ErrorNotSignedInDialog({
            titleText: "Already have a timetable or want one ?",
            // Template because the home url is dynamic
            messageText: _.template($("#js-templ-error-popup-not-signed-in-message").html(), data)
        }).show();
    };

    var exportToCalendar = function exportToCalendar(data) {
        return new ExportToCalendarDialog(data).show();
    };

    return _.extend(dialogFactory, {
        notSignedInError: notSignedInError,
        exportToCalendar: exportToCalendar
    });
});
