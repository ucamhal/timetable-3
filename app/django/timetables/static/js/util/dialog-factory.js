define([
    "jquery",
    "underscore",
    "view/dialog/error-dialog"
], function ($, _, ErrorDialog) {
    "use strict";

    var unknownError = function unknownError() {
        return new ErrorDialog({
            titleText: "The application has encountered an error",
            messageText: "It didn't affect your data, but our technical staff have been automatically notified and will be looking into this with the utmost urgency."
        }).show();
    };

    var sessionExpiredError = function sessionExpiredError(data) {
        return new ErrorDialog({
            titleText: "You've become signed out of Timetable",
            messageText: "Sign in again or reload the page to continue.",
            customFooterContent: _.template($("#js-templ-session-expired-error-popup-footer").html(), data),
            closeable: false
        }).show();
    };

    return {
        unknownError: unknownError,
        sessionExpiredError: sessionExpiredError
    };
});
