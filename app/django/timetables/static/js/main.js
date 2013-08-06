require.config({
    paths: {
        jquery: "libs/jquery-1.8.0",
        "jquery-bbq": "libs/jquery.bbq",
        underscore: "libs/underscore",
        backbone: "libs/backbone",
        bootstrap: "libs/bootstrap",
        bootstrapTypeahead: "libs/bootstrap-plugins/bootstrap-typeahead",
        fullcalendar: "libs/fullcalendar",
        "rangy-core": "libs/rangy-core"
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
        "rangy-core": {
            exports: "rangy"
        }
    }
});

define([
    "jquery",
    "util/shib-cookie-accumulation-workaround",
    "libs/jquery-django-csrf"
], function($, ShibCookieAccumulationWorkaround) {
    "use strict";

    // Enable the workaround for Shib setting loads of _shibstate_xxx cookies
    ShibCookieAccumulationWorkaround.preventShibFromDestroyingMyWebsite();

    // Define console.log to be an empty function in case it doesn't exist
    if (typeof window.console === "undefined") {
        window.console = {
            log: function () {}
        };
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

    // Work out what module was asked for and get require to load it.
    var $script = $("script[src$='require.js']"),
        indexName = $script.data("index"),
        pageName = $script.data("page");

    // If an index has been defined, load the appropriate file
    if (indexName) {
        console.log("Loading entry point: '" + indexName + "' with page: '" + pageName + "'");
        require([indexName], function (index) {
            index.initializePage(pageName);
        });
    }
});
