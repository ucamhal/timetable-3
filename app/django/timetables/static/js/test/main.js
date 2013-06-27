require.config({
    paths: {
        qunit: "test/libs/qunit"
    },

    shim: {
        qunit: {
            exports: "QUnit"
        }
    }
});

define([
    "qunit",
    "test/tests/calendarModel"
], function(qunit, calendarModel) {
    "use strict";
    qunit.init();
    calendarModel.test();
    qunit.start();
});
