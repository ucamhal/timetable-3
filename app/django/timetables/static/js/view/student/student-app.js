define([
    "jquery",
    "underscore",
    "backbone",
    "view/student/modules",
    "view/modules-selector",
    "view/calendar",
    "view/date-spinner",
    "model/calendarModel",
    "util/dialog-factory-student",
    "util/focus-helper",
    "util/page",
    "util/timetable-events",
    "util/jquery.select-text"
], function ($, _, Backbone, Modules, ModulesSelector, FullCalendarView, DateSpinner, CalendarModel, dialogFactory, focusHelper, page, timetableEvents) {
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

            this.$("li").removeClass("active").find("a").attr("aria-selected", "false");
            $target.addClass("active").find("a").attr("aria-selected", "true");

            var view = this.getViewFromTab($target);

            if(view) {
                timetableEvents.trigger("click_tab_"+view);
            }

            this.updateActiveView(view);

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
            _.bindAll(this);
            this.activeView = "agendaWeek";

            this.listView = new Modules.ListView({
                el: ".js-list-view",
                thingPath: this.getThingPath()
            });

            this.calendarViewNavigation = new CalendarViewNavigation({
                el: ".js-calendar-view-navigation"
            });

            this.modulesList = new Modules.ModulesList({
                el: ".js-modules-results",
                thingPath: this.getThingPath(),
                crsfToken: this.getCrsfToken()
            });

            this.modulesSelector = new ModulesSelector({
                el: ".js-modules-selector"
            });

            this.initCalendar();
            this.bindEvents();

            Backbone.history.start();
            this.calendarModel.setActiveDate(new Date());
        },

        initCalendar: function () {
            // Subtract the data from the html
            var rawTerms = $(".js-calendar").data("terms"),
                calendarStart = $.fullCalendar.parseDate($(".js-calendar").data("start")),
                calendarEnd = $.fullCalendar.parseDate($(".js-calendar").data("end")),
                terms = [];

            // Build the terms array based on the data found in the html
            _.each(rawTerms, function (term) {
                terms.push({
                    name: term.name,
                    start: $.fullCalendar.parseDate(term.start)
                });
            });

            this.calendarModel = new CalendarModel({
                terms: terms,
                start: calendarStart,
                end: calendarEnd
            });

            this.fullCalendarView = new FullCalendarView({
                el: ".js-calendar",
                eventsFeed: page.isUserLoggedIn() ? this.getThingPath() + ".cal.json" : undefined,
                defaultView: "agendaWeek",
                firstDay: 4
            });

            this.weekSpinner = new DateSpinner({
                el: ".js-date-spinner.js-agendaWeek"
            });

            this.termSpinner = new DateSpinner({
                el: ".js-date-spinner.js-term"
            });

            this.monthSpinner = new DateSpinner({
                el: ".js-date-spinner.js-month"
            });
        },

        onExportToCalendarClick: function (event) {
            timetableEvents.trigger("click_btn_export");
            var exportDialog = dialogFactory.exportToCalendar({
                userPath: this.getThingPath(),
                feedPath: $(event.currentTarget).data("feed-path")
            });

            this.listenTo(exportDialog, "feedChanged", this.onFeedChanged);
            this.listenTo(exportDialog, "close", this.onExportDialogClose);
        },

        onExportDialogClose: function () {
            focusHelper.focusTo($(".js-btn-export-to-calendar"));
        },

        onFeedChanged: function (feedPath) {
            $(".js-btn-export-to-calendar").data("feed-path", feedPath);
        },

        bindEvents: function () {
            this.listenTo(this.modulesSelector, "partChanged", this.partChangedHandler);
            this.listenTo(this.calendarViewNavigation, "viewChanged", this.viewChangedHandler);
            this.listenTo(this.modulesList, "timetableUpdated", this.timetableUpdatedHandler);

            this.listenTo(this.weekSpinner, "prev", this.onWeekPrev);
            this.listenTo(this.weekSpinner, "next", this.onWeekNext);

            this.listenTo(this.termSpinner, "prev", this.onTermPrev);
            this.listenTo(this.termSpinner, "next", this.onTermNext);

            this.listenTo(this.monthSpinner, "prev", this.onMonthPrev);
            this.listenTo(this.monthSpinner, "next", this.onMonthNext);

            this.listenTo(this.calendarModel, "change:activeDate", this.onActiveDateChange);
            this.listenTo(this.calendarModel, "change:activeTerm", this.onActiveTermChange);
            this.listenTo(this.calendarModel, "change:activeWeek", this.onActiveWeekChange);
            this.listenTo(this.calendarModel, "change:activeMonth", this.onActiveMonthChange);
            this.listenTo(this.calendarModel, "change:activeMonthTerm", this.onActiveMonthTermChange);


            $(".js-sign-out").on("click", this.onSignOutClick);
            $(".js-sign-in").on("click", this.onSignInClick);

            $(".js-btn-export-to-calendar").on("click", this.onExportToCalendarClick);

            $(window).on("resize", this.resize).trigger("resize");
        },

        onSignInClick: function (event) {
            timetableEvents.trigger("click_signin");
            this.onSignInOutClick(event);
        },

        onSignOutClick: function (event) {
            timetableEvents.trigger("click_signout");
            this.onSignInOutClick(event);
        },

        onSignInOutClick: function (event) {
            var $target = $(event.currentTarget),
                selection = Backbone.history.fragment ? "#" + Backbone.history.fragment : "";

            // Append the dropdown selection to the ?next part of the url
            window.location.href = $target.attr("href") + encodeURIComponent(selection);
            event.preventDefault();
        },

        onActiveDateChange: function (model, date) {
            this.fullCalendarView.goToDate(date);
            this.updateWeekSpinnerButtonStates();
            this.updateMonthSpinnerButtonStates();
            this.updateTermSpinnerButtonStates();
        },

        onActiveTermChange: function (model) {
            if (this.activeView === "agendaWeek") {
                this.updateTermSpinnerLabel(model.getActiveTermName());
            }
        },

        onActiveMonthTermChange: function (model) {
            if (this.activeView === "list" || this.activeView === "month") {
                this.updateTermSpinnerLabel(model.getActiveMonthTermName());
            }
        },

        updateTermSpinnerLabel: function (termName) {
            this.termSpinner.set({
                value: termName || "Outside term"
            });
        },

        onActiveWeekChange: function (model, activeWeek) {
            this.weekSpinner.set({
                value: activeWeek ? "Week " + activeWeek : "Outside term"
            });

            this.updateWeekSpinnerButtonStates();
        },

        onActiveMonthChange: function (model, activeMonth) {
            this.monthSpinner.set({
                value: activeMonth
            });
            this.updateMonthSpinnerButtonStates();

            if (this.activeView === "list") {
                this.listView.setActiveDate(model.getActiveDate());
            }
        },

        updateMonthSpinnerButtonStates: function () {
            var model = this.calendarModel,
                activeDate = model.getActiveDate(),
                nextMonth = model.moveDateToNextMonth(activeDate),
                prevMonth = model.moveDateToPrevMonth(activeDate),
                prevMonthPossible = model.isMonthWithinBoundaries(prevMonth),
                nextMonthPossible = model.isMonthWithinBoundaries(nextMonth);

            this.monthSpinner.set({
                prev: prevMonthPossible,
                next: nextMonthPossible
            });
        },

        updateTermSpinnerButtonStates: function () {
            var model = this.calendarModel,
                activeTerm = model.get("activeTerm"),
                activeDate;

            if (this.activeView === "month") {
                activeTerm = model.get("activeMonthTerm");
            }

            activeDate = activeTerm ? activeTerm.start : model.getActiveDate();

            this.termSpinner.set({
                prev: model.getPrevTermForDate(activeDate),
                next: model.getNextTermForDate(activeDate)
            });
        },

        updateWeekSpinnerButtonStates: function () {
            var model = this.calendarModel,
                activeDate = model.getActiveDate(),
                nextWeek = model.moveDateToNextWeek(activeDate),
                prevWeek = model.moveDateToPrevWeek(activeDate),
                prevWeekPossible = model.isCambridgeWeekWithinBoundaries(prevWeek),
                nextWeekPossible = model.isCambridgeWeekWithinBoundaries(nextWeek);

            this.weekSpinner.set({
                prev: prevWeekPossible,
                next: nextWeekPossible
            });
        },

        onWeekPrev: function () {
            this.calendarModel.goToPrevCambridgeWeek();
        },

        onWeekNext: function () {
            this.calendarModel.goToNextCambridgeWeek();
        },

        onMonthPrev: function () {
            this.calendarModel.goToPrevMonthFirstThursday();
        },

        onMonthNext: function () {
            this.calendarModel.goToNextMonthFirstThursday();
        },

        onTermPrev: function () {
            this.calendarModel.goToPrevTerm();
        },

        onTermNext: function () {
            this.calendarModel.goToNextTerm();
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
            if (this.fullCalendarView.eventPopup) {
                this.fullCalendarView.eventPopup.toggle(false);
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
                    this.thingPath = "user/" + $("#userinfo").data("userid");
                } else if ($("#thinginfo").length === 1) {
                    this.thingPath = $("#thinginfo").data("fullpath");
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
            if(fullpath !== "") {
                timetableEvents.trigger("part_change", fullpath);
            }

            this.navigate(fullpath, {
                trigger: true
            });
        },

        viewChangedHandler: function (activeView) {
            if (this.activeView !== activeView) {
                this.activeView = activeView;

                switch (activeView) {
                case "month":
                    this.listView.hide();
                    $(".js-agendaWeek", ".js-calendar-navigation").hide();

                    $(".js-month, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.show();
                    this.fullCalendarView.setView("month");

                    this.updateTermSpinnerLabel(this.calendarModel.getActiveMonthTermName());
                    this.updateTermSpinnerButtonStates();
                    break;
                case "list":
                    this.fullCalendarView.hide();
                    $(".js-agendaWeek", ".js-calendar-navigation").hide();

                    $(".js-month, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.setView("month");

                    this.listView.setActiveDate(this.calendarModel.getActiveDate());
                    this.listView.show();

                    this.updateTermSpinnerLabel(this.calendarModel.getActiveMonthTermName());
                    this.updateTermSpinnerButtonStates();
                    break;
                case "agendaWeek":
                    $(".js-month", ".js-calendar-navigation").hide();
                    this.listView.hide();

                    $(".js-agendaWeek, .js-term", ".js-calendar-navigation").show();
                    this.fullCalendarView.show();
                    this.fullCalendarView.setView("agendaWeek");

                    this.updateTermSpinnerLabel(this.calendarModel.getActiveTermName());
                    this.updateTermSpinnerButtonStates();
                    break;
                }
            }
        }
    });


    return {
        Application: Application
    };

});
