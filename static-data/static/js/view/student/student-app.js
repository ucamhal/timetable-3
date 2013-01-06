define([
    "jquery",
    "underscore",
    "backbone",
    "view/student/modules",
    "view/admin/calendar",
    "view/cookieHandler"
], function ($, _, Backbone, modules, calendar, CookieHandler) {

    var Application = Backbone.Router.extend({
        initialize: function () {
            _.bindAll(this, "partChangedHandler");

            this.cookieHandler = new CookieHandler({
                el: ".js-cookie-alert"
            });

            this.modulesList = new modules.ModulesList({
                el: ".js-modules-list"
            });

            this.modulesSelector = new modules.ModulesSelector({
                el: ".js-modules-selector"
            });

            Backbone.history.start();

            this.modulesSelector.on("partChanged", this.partChangedHandler);
        },

        routes: {
            "tripos/*fullpath" : "updateShownModules"
        },

        updateShownModules: function (fullpath) {
            this.modulesList.updateList("tripos/" + fullpath);
            this.modulesSelector.setSelectsFromFullpath("tripos/" + fullpath);
        },

        partChangedHandler: function (fullpath) {
            this.navigate(fullpath, {
                trigger: true
            });
        }
    });


    return {
        Application: Application
    };

});
