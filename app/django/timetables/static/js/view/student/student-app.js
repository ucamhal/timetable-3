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

        getActiveView: function () {
            return this.getViewFromTab(this.$(".active"));
        },

        setActiveView: function (view) {
            var tabClassName = _.invert(this.tabClassToView)[view];
            if (tabClassName) {
                this.$("." + tabClassName).trigger("click");
            }
        },

        getViewFromTab: function ($tab) {
            var classes = $tab.attr("class").split(/\s+/),
                self = this,
                tabClass = _.find(classes, function (className) {
                    return _.has(self.tabClassToView, className);
                });

            return this.tabClassToView[tabClass];
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
            this.bindMediaEvents();

            Backbone.history.start();
            this.calendarModel.setActiveDate(new Date());
        },

        bindMediaEvents: function () {
            if (typeof window.matchMedia === "function") {
                var self = this;
                // Listen to changes on the mql object:
                // The mql object is created by providing a set of media querries
                // it must match. If at any point the list is matched the "matches"
                // boolean on the object is set to true. If matches changes, it will
                // dispatch an event to all attached listeners.
                // More info:
                // http://dev.w3.org/csswg/cssom-view/#the-mediaquerylist-interface
                window.matchMedia("print").addListener(function (mediaQueryList) {
                    if (mediaQueryList.matches) {
                        self.onBeforePrint();
                    } else {
                        self.onAfterPrint();
                    }
                });
            }

            // IE and FF support:
            window.onbeforeprint = this.onBeforePrint;
            window.onafterprint = this.onAfterPrint;
        },

        onBeforePrint: (function () {
            // Debounce because chrome triggers it multiple times for the same
            // print dialog.
            var debouncedTrigger = _.debounce(function (event) {
                timetableEvents.trigger(event);
            }, 200);

            return function () {
                debouncedTrigger("on_before_print");
                if (this.activeView === "month") {
                    this.switchToMonthAfterPrint = true;
                    this.calendarViewNavigation.setActiveView("agendaWeek");
                }
                this.printResize();
            };
        }()),

        onAfterPrint: function () {
            this.resize();
            // Fixes a fullcalendar bug which nicely cutted off part of the
            // calendar.
            var fcHeight = this.fullCalendarView.$el.fullCalendar("option", "height");
            this.fullCalendarView.setHeight(fcHeight);

            if (this.switchToMonthAfterPrint) {
                this.switchToMonthAfterPrint = false;
                this.calendarViewNavigation.setActiveView("month");
            }
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

        onPrintClick: function () {
            timetableEvents.trigger("click_btn_print");
            window.print();
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
            $(".js-btn-print").on("click", this.onPrintClick);
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

        printResize: function () {
            switch (this.activeView) {
            case "agendaWeek":
                $("#calendarHolder").width(910);
                var calendarView = this.fullCalendarView.getView(),
                    elHeight = calendarView.element.find(".fc-agenda-slots").outerHeight(true),
                    // The days row height is independant from the agenda slots
                    // but it's still needed for the calendar height calculation so
                    // we have to include it in our calculation:
                    daysTable = calendarView.element.find(".fc-agenda-days"),
                    // The days row is in the table <thead>, we can't calculate the
                    // <thead> height directly because it wouldn't include table
                    // borders, etc.
                    daysRowHeight = daysTable.height() - daysTable.find("tbody").height();
                this.fullCalendarView.setHeight(elHeight + daysRowHeight + 1);
                $("#calendar").fullCalendar("render");
                break;
            case "list":
                $("#calendarHolder").css("width", "auto");
                break;
            }
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
            // Have a minimum height of 300
            if (modulesListHeight < 300) {
                modulesListHeight = 300;
            }

            $(".js-modules-results").height(modulesListHeight);
            $("#inputArea > div").width(maxWidth);
            $("#uniLogo").width(maxWidth);
            $("#content").width(maxWidth);
            $("#actionsContainer").width(maxWidth);
            $("#calendarHolder").width(maxWidth - this.modulesList.$el.outerWidth() - 50);

            $(".js-calendar-holder").height(modulesListHeight);

            this.listView.setHeight(modulesListHeight - this.calendarViewNavigation.$el.outerHeight() - $(".js-calendar-navigation").outerHeight() - 17);
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
