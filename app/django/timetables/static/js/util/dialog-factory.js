define([
    "jquery",
    "underscore",
    "view/dialog/error-dialog",
    "view/dialog/remove-dialog"
], function ($, _, ErrorDialog, RemoveDialog) {
    "use strict";

    var saveLinkError = function saveLinkError(data) {
        return new ErrorDialog({
            titleText: _.template($("#js-templ-error-popup-save-link-title").text(), data),
            messageText: _.template($("#js-templ-error-popup-save-link-message").text(), data)
        });
    };

    var saveLinkSelectError = function saveLinkSelectError() {
        return new ErrorDialog({
            titleText: "Can't save link",
            messageText: "Please select both a module and a part before saving the link."
        });
    };

    var saveLinkClashError = function saveLinkClashError() {
        return new ErrorDialog({
            titleText: "Can't save link",
            messageText: "The selected part is already linked to your timetable."
        });
    };

    var saveLinkTimetableError = function saveLinkTimetableError() {
        return new ErrorDialog({
            titleText: "Can't save link",
            messageText: "You cannot link a timetable to itself."
        });
    };

    var removeLink = function removeLink(data) {
        return new RemoveDialog({
            titleText: _.template($("#js-templ-remove-link-popup-title").text(), data),
            contentsText: _.template($("#js-templ-remove-link-popup-contents").text(), data),
            confirmBtnText: _.template($("#js-templ-remove-link-popup-btn-confirm").text(), data),
            errorText: _.template($("#js-templ-remove-link-popup-error").text(), data),
            removingTitleText: _.template($("#js-templ-remove-link-popup-removing-title").text(), data)
        });
    };

    var removeModule = function removeModule(data) {
        return new RemoveDialog({
            titleText: _.template($("#js-templ-remove-module-series-popup-title").text(), data),
            contentsText: _.template($("#js-templ-remove-module-popup-contents").text(), data),
            confirmBtnText: _.template($("#js-templ-remove-module-series-popup-btn-confirm").text(), data),
            errorText: _.template($("#js-templ-remove-module-series-popup-error").text(), data),
            removingTitleText: _.template($("#js-templ-remove-module-series-popup-removing-title").text(), data)
        });
    };

    var removeSeries = function removeSeries(data) {
        return new RemoveDialog({
            titleText: _.template($("#js-templ-remove-module-series-popup-title").text(), data),
            contentsText: _.template($("#js-templ-remove-series-popup-contents").text(), data),
            confirmBtnText: _.template($("#js-templ-remove-module-series-popup-btn-confirm").text(), data),
            errorText: _.template($("#js-templ-remove-module-series-popup-error").text(), data),
            removingTitleText: _.template($("#js-templ-remove-module-series-popup-removing-title").text(), data)
        });
    };

    return {
        saveLinkError: saveLinkError,
        saveLinkSelectError: saveLinkSelectError,
        saveLinkClashError: saveLinkClashError,
        saveLinkTimetableError: saveLinkTimetableError,
        removeLink: removeLink,
        removeModule: removeModule,
        removeSeries: removeSeries
    };
});
