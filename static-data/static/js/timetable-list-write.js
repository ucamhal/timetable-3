define(["view/admin/lists", "bootstrap", "not-implemented-tooltips"],
		function(Lists) {
    "use strict";

    $(".js-module").each(function() {
        new Lists.WritableModuleView({el: this});
    });

    $(".js-series").each(function() {
        new Lists.WritableSeriesView({el: this});
    });

    // Make the list watch for URL hash items in order to expand series
    // & highlight events.
    Lists.bindUrlHashWatcher();

    // Fire an initial hashchange to handle hash params in the URL on
    // page load.
    $(window).trigger("hashchange");

    return undefined;
});
