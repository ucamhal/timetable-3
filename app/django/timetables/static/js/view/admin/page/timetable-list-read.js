define([
    "jquery",
    "view/admin/lists",
    "bootstrap"
], function($, Lists) {
    "use strict";

    $(".js-module").each(function() {
        new Lists.ModuleView({el: this});
    });

    // Make the list watch for URL hash items in order to expand series
    // & highlight events.
    Lists.bindUrlHashWatcher();

    // Fire an initial hashchange to handle hash params in the URL on
    // page load.
    $(window).trigger("hashchange");

    return undefined;
});
