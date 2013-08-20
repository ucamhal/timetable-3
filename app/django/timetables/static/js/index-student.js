define([
    "backbone",
    "view/student/student-app",
    "view/cookieHandler",
    "util/canary-watcher",
    "util/dialog-factory-student",
    "util/page"
], function(Backbone, studentApp, CookieHandler, canaryWatcher, dialogFactory, page) {
    "use strict";

    var initializePage = function initializePage() {
        // Only watch the canary if the user is logged in.
        if (page.isUserLoggedIn()) {
            canaryWatcher.startWatch(function () {
                // Stop watching
                canaryWatcher.stopWatch();
                // Remember the selected timetable
                var fullpath = Backbone.history.fragment ? "#" + Backbone.history.fragment : "";
                // Show the session expired popup
                dialogFactory.sessionExpiredError({
                    returnURL: window.location.pathname + fullpath
                });
            });
        }

        new CookieHandler({
            el: ".js-cookie-alert"
        });

        new studentApp.Application();
    };

    return {
        initializePage: initializePage
    };
});
