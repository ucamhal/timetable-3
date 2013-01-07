define([
    "jquery",
    "underscore",
    "backbone",
    "view/student/modules",
    "view/admin/calendar",
    "view/cookieHandler"
], function ($, _, Backbone, Modules, Calendar, CookieHandler) {

    "use strict";

    var CalendarViewNavigation = Backbone.View.extend({
        initialize: function () {

        },

        tabClassToView: {
            "js-week" : "agendaWeek",
            "js-month" : "month",
            "js-list" : "list"
        },

        events: {
            "click li" : "tabClickHandler"
        },

        tabClickHandler: function (event) {
            var $target = $(event.currentTarget);
            
            this.$("li").removeClass("active");
            $target.addClass("active");

            this.updateActiveView(this.getViewFromTab($target));

            event.preventDefault();
        },

        getViewFromTab: function ($tab) {
            var classes = $tab.attr("class").split(/\s+/),
                i;
            
            for (i = 0; i < classes.length; i += 1) {
                if (this.tabClassToView.hasOwnProperty(classes[i])) {
                    return this.tabClassToView[classes[i]];
                }
            }

            return undefined;
        },

        updateActiveView: function (viewToSet) {
            if (viewToSet !== this.activeView) {
                this.activeView = viewToSet;
                this.trigger("viewChanged", this.activeView);
            }
        }
    });

    var Application = Backbone.Router.extend({
        initialize: function () {
            _.bindAll(this, "partChangedHandler");
            _.bindAll(this, "timetableUpdatedHandler");
            _.bindAll(this, "viewChangedHandler");

            console.log("thingPath: " + this.getThingPath());

            this.fullCalendarView = new Calendar.FullCalendarView({
                el: ".js-calendar",
                eventsFeed: this.getThingPath() + ".cal.json",
                defaultView: "agendaWeek"
            });

            this.calendarViewNavigation = new CalendarViewNavigation({
                el: ".js-calendar-view-navigation"
            });

            this.cookieHandler = new CookieHandler({
                el: ".js-cookie-alert"
            });

            this.modulesList = new Modules.ModulesList({
                el: ".js-modules-list",
                thingPath: this.getThingPath(),
                crsfToken: this.getCrsfToken()
            });

            this.modulesSelector = new Modules.ModulesSelector({
                el: ".js-modules-selector"
            });

            Backbone.history.start();

            this.modulesSelector.on("partChanged", this.partChangedHandler);
            this.calendarViewNavigation.on("viewChanged", this.viewChangedHandler);
            this.modulesList.on("timetableUpdated", this.timetableUpdatedHandler);

            this.viewChangedHandler("agendaWeek");
        },

        timetableUpdatedHandler: function () {
            this.fullCalendarView.refresh();
        },

        getCrsfToken: function () {
            if (!this.crsfToken) {
                if ($("#userinfo").length === 1) {
                    this.crsfToken = $("#userinfo").find("[name=csrfmiddlewaretoken]").val();
                } else if ($("#thinginfo").length === 1) {
                    this.crsfToken = $("#thinginfo").find("[name=csrfmiddlewaretoken]").val();
                }
            }

            return this.crsfToken;
        },

        getThingPath: function () {
            if (!this.thingPath) {
                if ($("#userinfo").length === 1) {
                    this.thingPath = "user/" + $("#userinfo").attr("userid");
                } else if ($("#thinginfo").length === 1) {
                    this.thingPath = $("#thinginfo").attr("fullpath");
                }
            }

            return this.thingPath;
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
        },

        viewChangedHandler: function (activeView) {
            switch (activeView) {
                case "month":
                    $(".js-agendaWeek", ".js-calendar-navigation").hide()
                    $(".js-month, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.setView(activeView);
                    break;
                case "agendaWeek":
                    $(".js-month", ".js-calendar-navigation").hide()
                    $(".js-agendaWeek, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.setView(activeView);
                    break;
                case "list":
                    break;
            }
        }
    });


    return {
        Application: Application
    };

});
