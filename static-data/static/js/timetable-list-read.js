define([
    "view/admin/lists",
    "view/cookieHandler",
    "bootstrap",
    "not-implemented-tooltips"
], function(Lists, CookieHandler) {
    "use strict";

    $(".js-module").each(function() {
        new Lists.ModuleView({el: this});
    });

    $(".js-series").each(function() {
        new Lists.SeriesView({el: this});
    });

    var cookieHandler = new CookieHandler({
        el: ".js-cookie-alert"
    });
    
    // Make the list watch for URL hash items in order to expand series
    // & highlight events.
    Lists.bindUrlHashWatcher();

    // Fire an initial hashchange to handle hash params in the URL on
    // page load.
    $(window).trigger("hashchange");

    return undefined;
});
