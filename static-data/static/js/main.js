var require;

// Configure RequireJS (almost boilerplate)
require.config({
    paths: {
        domReady: "libs/domReady",
        jquery: "libs/jquery-1.8.0",
        "jquery-ui": "libs/jquery-ui/jquery-ui-1.8.23.custom.min",
        "jquery-bbq": "libs/jquery.bbq",
        underscore: "libs/underscore",
        bootstrap: "libs/bootstrap",
        bootstrapDatePicker: "libs/bootstrap-plugins/bootstrap-datepicker",
        bootstrapTimePicker: "libs/bootstrap-plugins/bootstrap-timepicker",
        fullcalendar: "libs/fullcalendar"
    },
    shim: {
        jquery: {
            exports: "$"
        },
        "underscore": {
            exports: "_"
        },
        "bootstrap": {
            deps: ["jquery"]
        },
        "fullcalendar" : {
            deps: ["jquery"]
        }
    }
});

require([
  "jquery",
  "domReady"
], function($) {
   "use strict";

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
