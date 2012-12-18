var require;

// Configure RequireJS (almost boilerplate)
require.config({
    paths: {
        domReady: "libs/domReady",
        jquery: "libs/jquery-1.8.0",
        "jquery-ui": "libs/jquery-ui/jquery-ui-1.8.23.custom.min",
        "jquery-bbq": "libs/jquery.bbq",
        underscore: "libs/underscore",
        backbone: "libs/backbone",
        bootstrap: "libs/bootstrap",
        bootstrapDatePicker: "libs/bootstrap-plugins/bootstrap-datepicker",
        bootstrapTimePicker: "libs/bootstrap-plugins/bootstrap-timepicker",
        bootstrapSpinner: "libs/bootstrap-plugins/bootstrap-spinner",
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

require([
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
   if(!page_module) {
       console.log("No Script for page was defined in the html scipt tag where require.js was loaded from add data-page-module='nameofmodule' " + 
               "require.js's script tag.");
       return;
   }

   console.log("Loading entry point:", page_module);
   // Load the module defined as the page's entry point, but dont attach to the event thats loading the rest of the page.
   window.setTimeout(function() {
       require([page_module], function(page_module) {
             // that should be enough to get it loaded.
          });
       },10);



});
