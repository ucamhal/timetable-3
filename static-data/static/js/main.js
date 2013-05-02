require.config({
    paths: {
        domReady: "libs/domReady",
        jquery: "libs/jquery-1.8.0",
        "jquery-bbq": "libs/jquery.bbq",
        underscore: "libs/underscore",
        backbone: "libs/backbone",
        bootstrap: "libs/bootstrap",
        bootstrapTypeahead: "libs/bootstrap-plugins/bootstrap-typeahead",
        fullcalendar: "libs/fullcalendar"
    },
    shim: {
        jquery: {
            exports: "$"
        },
        "underscore": {
            exports: "_"
        },
        "backbone": {
            exports: "Backbone",
            deps: ["jquery", "underscore"]
        },
        "bootstrap": {
            deps: ["jquery"]
        },
        "fullcalendar" : {
            deps: ["jquery"]
        },
        "libs/jquery-django-csrf": {
            deps: ["jquery"]
        },
    }
});

define([
    "jquery",
    "libs/jquery-django-csrf",
    "domReady"
], function($) {
    "use strict";

    //Define console.log to be an empty function in case it doesn't exist
    if (typeof window.console === "undefined") {
        window.console = {
            log: function () {}
        };
    }

    // work out what module was asked for and get require to load it.
    var page_module = $("script[src$='require.js']").attr("data-page-module");
    if (!page_module) {
        console.log("No Script for page was defined in the html scipt tag where require.js was loaded from add data-page-module='nameofmodule' require.js's script tag.");
        return;
    }

    // Load the module defined as the page's entry point, but dont attach to the event thats loading the rest of the page.
    window.setTimeout(function() {
        console.log("Loading entry point:", page_module);
        require([page_module]);
    },10);
});
