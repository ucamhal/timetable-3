require.config({
    paths: {
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
        }
    }
});

define([
    "jquery",
    "libs/jquery-django-csrf"
], function($) {
    "use strict";

    // Define console.log to be an empty function in case it doesn't exist
    if (typeof window.console === "undefined") {
        window.console = {
            log: function () {}
        };
    }

    // Work out what module was asked for and get require to load it.
    var page_module = $("script[src$='require.js']").attr("data-page-module");
    if (!page_module) {
        console.log("No Script for page was defined in the html scipt tag where require.js was loaded from add data-page-module='nameofmodule' require.js's script tag.");
        return;
    }

    // Check if "".trim() exists
    if (typeof String.prototype.trim !== "function") {
        String.prototype.trim = function () {
            return this.replace(/^\s+|\s+$/g, "");
        };
    }

    // Check if Function.prototype.bind exists
    if (typeof Function.prototype.bind !== "function") {
        Function.prototype.bind= function(owner) {
            var that = this;
            if (arguments.length<=1) {
                return function() {
                    return that.apply(owner, arguments);
                };
            } else {
                var args= Array.prototype.slice.call(arguments, 1);
                return function() {
                    return that.apply(owner, arguments.length === 0 ? args : args.concat(Array.prototype.slice.call(arguments)));
                };
            }
        };
    }

    // Load the module defined as the page's entry point, but dont attach to the event thats loading the rest of the page.
    window.setTimeout(function() {
        console.log("Loading entry point:", page_module);
        require([page_module]);
    },10);
});
