define(["bootstrap"], function() {
    "use strict";

    // Show tooltips on all elements w/ class notImplemented (delegated)
    $(document).tooltip({
        title: "Not yet implemented.",
        selector: ".notImplemented"
    });
});
