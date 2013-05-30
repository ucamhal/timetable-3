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
            var self = this;

            _.bindAll(this, "partChangedHandler");
            _.bindAll(this, "timetableUpdatedHandler");
            _.bindAll(this, "viewChangedHandler");
            _.bindAll(this, "resize");

            this.fullCalendarView = new Calendar.FullCalendarView({
                el: ".js-calendar",
                eventsFeed: this.getThingPath() + ".cal.json",
                defaultView: "agendaWeek",
                firstDay: 4
            });

            this.listView = new Modules.ListView({
                el: ".js-list-view",
                thingPath: this.getThingPath()
            });

            this.calendarViewNavigation = new CalendarViewNavigation({
                el: ".js-calendar-view-navigation"
            });

            this.cookieHandler = new CookieHandler({
                el: ".js-cookie-alert"
            });

            this.modulesList = new Modules.ModulesList({
                el: ".js-modules-results",
                thingPath: this.getThingPath(),
                crsfToken: this.getCrsfToken()
            });

            this.modulesSelector = new Modules.ModulesSelector({
                el: ".js-modules-selector"
            });

            $.get("/static/js/data/terms.json", function (terms) {
                self.weekSpinner = new Calendar.DateSpinner({
                    el: ".js-date-spinner.js-agendaWeek",
                    type: "week",
                    calendar: self.fullCalendarView,
                    terms: terms
                }),

                self.termSpinner = new Calendar.DateSpinner({
                    el: ".js-date-spinner.js-term",
                    type: "term",
                    calendar: self.fullCalendarView,
                    terms: terms
                });

                self.monthSpinner = new Calendar.DateSpinner({
                    el: ".js-date-spinner.js-month",
                    type: "month",
                    calendar: self.fullCalendarView,
                    terms: terms
                });

                self.calendarSpinners = [
                    self.weekSpinner,
                    self.termSpinner,
                    self.monthSpinner
                ];

                self.weekSpinner.on("change", _.bind(self.renderSpinners, self, self.weekSpinner));
                self.termSpinner.on("change", _.bind(self.renderSpinners, self, self.termSpinner));
                self.monthSpinner.on("change", _.bind(self.renderSpinners, self, self.monthSpinner));
            });

            Backbone.history.start();

            this.modulesSelector.on("partChanged", this.partChangedHandler);
            this.calendarViewNavigation.on("viewChanged", this.viewChangedHandler);
            this.modulesList.on("timetableUpdated", this.timetableUpdatedHandler);

            $(window).on("resize", this.resize);
            this.resize();
        },

        resize: function () {
            var windowWidth = $(window).width(),
                windowHeight = $(window).height(),
                maxWidth = windowWidth - 200,

                modulesListHeight,
                footerHeight = $(".footer-wrap").outerHeight();

            if(maxWidth < 960) {
                maxWidth = 960;
            } else if (maxWidth > 1400) {
                maxWidth = 1400;
            }

            modulesListHeight = windowHeight - footerHeight - this.modulesList.$el.offset().top - 30;
            modulesListHeight = $(".js-modules-results").height(modulesListHeight).height();

            $("#inputArea > div").width(maxWidth);
            $("#uniLogo").width(maxWidth);
            $("#content").width(maxWidth);
            $("#actionsContainer").width(maxWidth);
            $("#calendarHolder").width(maxWidth - this.modulesList.$el.outerWidth() - 50);

            $(".js-calendar-holder").height(modulesListHeight);
            $(".js-list-view").height(modulesListHeight - this.calendarViewNavigation.$el.outerHeight() - $(".js-calendar-navigation").outerHeight() - 17);
            this.fullCalendarView.setHeight(modulesListHeight - this.calendarViewNavigation.$el.outerHeight() - $(".js-calendar-navigation").outerHeight() - 17);
            this.fullCalendarView.eventPopup.hide();

        },

        renderSpinners: function (changedSpinner) {
            _.each(this.calendarSpinners, function (spinner) {
                if (spinner !== changedSpinner) {
                    spinner.render();
                }
            });

            if (this.activeView === "list") {
                this.listView.setActiveDate(this.fullCalendarView.getActiveDate());
            }
        },

        timetableUpdatedHandler: function () {
            this.fullCalendarView.refresh();

            if (this.activeView === "list") {
                this.listView.render();
            }
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
            if (this.activeView !== activeView) {
                this.activeView = activeView;

                switch (activeView) {
                case "month":
                    $(".js-agendaWeek", ".js-calendar-navigation").hide();
                    this.listView.hide();
                    $(".js-month, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.show();
                    this.fullCalendarView.setView("month");
                    break;
                case "list":
                    $(".js-agendaWeek", ".js-calendar-navigation").hide();
                    this.fullCalendarView.hide();
                    $(".js-month, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.setView("month");
                    this.listView.setActiveDate(this.fullCalendarView.getActiveDate());
                    this.listView.show();
                    break;
                case "agendaWeek":
                    $(".js-month", ".js-calendar-navigation").hide();
                    this.listView.hide();
                    $(".js-agendaWeek, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.show();
                    this.fullCalendarView.setView(activeView);
                    break;
                }

                this.renderSpinners();
                this.termSpinner.updateActiveTermData();
            }
        }
    });


    return {
        Application: Application
    };

});
