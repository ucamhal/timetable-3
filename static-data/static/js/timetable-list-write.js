define(["view/admin/lists", "bootstrap", "not-implemented-tooltips"],
		function(Lists) {
    "use strict";

    $(".js-module").each(function() {
        new Lists.WritableModuleView({el: this});
    });

    $(".js-series").each(function() {
        new Lists.WritableSeriesView({el: this});
    });

    return undefined;
});
