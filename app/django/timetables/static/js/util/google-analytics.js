define([], function () {
    "use strict";

    var ga;

    window.GoogleAnalyticsObject = "ga";
    window.ga = window.ga || function () {
        // set up a queue for tracked events which analytics.js can handle once
        // it's loaded.
        (window.ga.q = window.ga.q || []).push(arguments);
    };

    window.ga.l = 1 * new Date();

    // Set up a function to return the GA function so other modules don't need
    // to access the window.ga global
    ga = function () {
        window.ga.apply(this, arguments);
    };

    // Load the analytics code
    require(["http://www.google-analytics.com/analytics.js"]);

    return ga;
});
