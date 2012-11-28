define(["bootstrap", "view/admin/lists"], function(Classes, Lists) {
    "use strict";

    $(".js-module").each(function() {
        new Lists.ModuleView({el: this});
    });

    $(".js-series").each(function() {
        new Lists.SeriesView({el: this});
    });

    return undefined;
});