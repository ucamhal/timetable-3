define([
    "jquery",
    "underscore",
    "view/dialog/error-dialog",
    "view/dialog/remove-dialog"
], function ($, _, ErrorDialog, RemoveDialog) {
    "use strict";

    var saveLinkError = function saveLinkError(data) {
        return new ErrorDialog({
            titleText: _.template($("#js-templ-error-popup-save-link-title").html(), data),
            messageText: _.template($("#js-templ-error-popup-save-link-message").html(), data)
        }).show();
    };

    var saveLinkSelectError = function saveLinkSelectError() {
        return new ErrorDialog({
            titleText: "Can't save link",
            messageText: "Please select both a module and a part before saving the link."
        }).show();
    };

    var saveLinkClashError = function saveLinkClashError() {
        return new ErrorDialog({
            titleText: "Can't save link",
            messageText: "The selected part is already linked to your timetable."
        }).show();
    };

    var saveLinkTimetableError = function saveLinkTimetableError() {
        return new ErrorDialog({
            titleText: "Can't save link",
            messageText: "You cannot link a timetable to itself."
        }).show();
    };

    var sessionExpiredError = function sessionExpiredError(data) {
        return new ErrorDialog({
            titleText: "You've become signed out of Timetable",
            messageText: "Sign in again or reload the page to continue.",
            customFooterContent: _.template($("#js-templ-session-expired-error-popup-footer").html(), data),
            closeable: false
        });
    };

    var eventInvalidDataError = function eventInvalidDataError() {
        return new ErrorDialog({
            titleText: "Invalid event data",
            messageText: "Please provide a title for each event before saving."
        }).show();
    };

    var removeLink = function removeLink(data) {
        return new RemoveDialog({
            titleText: _.template($("#js-templ-remove-link-popup-title").html(), data),
            contentsText: _.template($("#js-templ-remove-link-popup-contents").html(), data),
            confirmBtnText: _.template($("#js-templ-remove-link-popup-btn-confirm").html(), data),
            errorText: _.template($("#js-templ-remove-link-popup-error").html(), data),
            removingTitleText: _.template($("#js-templ-remove-link-popup-removing-title").html(), data)
        }).show();
    };

    var removeModule = function removeModule(data) {
        return new RemoveDialog({
            titleText: _.template($("#js-templ-remove-module-series-popup-title").html(), data),
            contentsText: _.template($("#js-templ-remove-module-popup-contents").html(), data),
            confirmBtnText: _.template($("#js-templ-remove-module-series-popup-btn-confirm").html(), data),
            errorText: _.template($("#js-templ-remove-module-series-popup-error").html(), data),
            removingTitleText: _.template($("#js-templ-remove-module-series-popup-removing-title").html(), data)
        }).show();
    };

    var removeSeries = function removeSeries(data) {
        return new RemoveDialog({
            titleText: _.template($("#js-templ-remove-module-series-popup-title").html(), data),
            contentsText: _.template($("#js-templ-remove-series-popup-contents").html(), data),
            confirmBtnText: _.template($("#js-templ-remove-module-series-popup-btn-confirm").html(), data),
            errorText: _.template($("#js-templ-remove-module-series-popup-error").html(), data),
            removingTitleText: _.template($("#js-templ-remove-module-series-popup-removing-title").html(), data)
        }).show();
    };

    return {
        saveLinkError: saveLinkError,
        saveLinkSelectError: saveLinkSelectError,
        saveLinkClashError: saveLinkClashError,
        saveLinkTimetableError: saveLinkTimetableError,
        sessionExpiredError: sessionExpiredError,
        eventInvalidDataError: eventInvalidDataError,
        removeLink: removeLink,
        removeModule: removeModule,
        removeSeries: removeSeries
    };
});
