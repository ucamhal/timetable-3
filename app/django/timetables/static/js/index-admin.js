define([
    "view/cookieHandler",
    "util/canary-watcher",
    "util/dialog-factory",
    "util/page"
], function (CookieHandler, canaryWatcher, dialogFactory, page) {
    "use strict";

    var initializePage = function initializePage(pageName) {

        // Only initialize the canaryWatcher if the user is logged in.
        if (page.isUserLoggedIn()) {
            canaryWatcher.startWatch(function () {
                // Stop the watch
                canaryWatcher.stopWatch();
                // Show the session expired popup
                dialogFactory.sessionExpiredError({
                    returnURL: window.location.pathname
                });
            });
        }

        new CookieHandler({
            el: ".js-cookie-alert"
        });

        require(["view/admin/page/" + pageName]);
    };

    return {
        initializePage: initializePage
    };
});
