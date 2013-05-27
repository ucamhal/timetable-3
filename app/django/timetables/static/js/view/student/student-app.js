define([
    "jquery",
    "underscore",
    "backbone",
    "view/student/modules",
    "view/admin/calendar",
    "view/cookieHandler"
], function ($, _, Backbone, Modules, Calendar, CookieHandler) {
    "use strict";

    var terms = {
        "2011": {
            "michaelmas": {
                "1": "2011-10-06",
                "2": "2011-10-13",
                "3": "2011-10-20",
                "4": "2011-10-27",
                "5": "2011-11-03",
                "6": "2011-11-10",
                "7": "2011-11-17",
                "8": "2011-11-24"
            },
            "lent": {
                "1": "2012-01-19",
                "2": "2012-01-26",
                "3": "2012-02-02",
                "4": "2012-02-09",
                "5": "2012-02-16",
                "6": "2012-02-23",
                "7": "2012-03-01",
                "8": "2012-03-08"
            },
            "easter": {
                "1": "2012-04-26",
                "2": "2012-05-03",
                "3": "2012-05-10",
                "4": "2012-05-17",
                "5": "2012-05-24",
                "6": "2012-05-31",
                "7": "2012-06-07",
                "8": "2012-06-14"
            }
        },
        "2012": {
            "michaelmas": {
                "1": "2012-10-04",
                "2": "2012-10-11",
                "3": "2012-10-18",
                "4": "2012-10-25",
                "5": "2012-11-01",
                "6": "2012-11-08",
                "7": "2012-11-15",
                "8": "2012-11-22"
            },
            "lent": {
                "1": "2013-01-17",
                "2": "2013-01-24",
                "3": "2013-01-31",
                "4": "2013-02-07",
                "5": "2013-02-14",
                "6": "2013-02-21",
                "7": "2013-02-28",
                "8": "2013-03-07"
            },
            "easter": {
                "1": "2013-04-25",
                "2": "2013-05-02",
                "3": "2013-05-09",
                "4": "2013-05-16",
                "5": "2013-05-23",
                "6": "2013-05-30",
                "7": "2013-06-06",
                "8": "2013-06-13"
            }
        },
        "2013": {
            "michaelmas": {
                "1": "2013-10-10",
                "2": "2013-10-17",
                "3": "2013-10-24",
                "4": "2013-10-31",
                "5": "2013-11-07",
                "6": "2013-11-14",
                "7": "2013-11-21",
                "8": "2013-11-28"
            },
            "lent": {
                "1": "2014-01-16",
                "2": "2014-01-23",
                "3": "2014-01-30",
                "4": "2014-02-06",
                "5": "2014-02-13",
                "6": "2014-02-20",
                "7": "2014-02-27",
                "8": "2014-03-06"
            },
            "easter": {
                "1": "2014-04-24",
                "2": "2014-05-01",
                "3": "2014-05-08",
                "4": "2014-05-15",
                "5": "2014-05-22",
                "6": "2014-05-29",
                "7": "2014-06-05",
                "8": "2014-06-12"
            }
        },
        "2014": {
            "michaelmas": {
                "1": "2014-10-09",
                "2": "2014-10-16",
                "3": "2014-10-23",
                "4": "2014-10-30",
                "5": "2014-11-06",
                "6": "2014-11-13",
                "7": "2014-11-20",
                "8": "2014-11-27"
            },
            "lent": {
                "1": "2015-01-15",
                "2": "2015-01-22",
                "3": "2015-01-29",
                "4": "2015-02-05",
                "5": "2015-02-12",
                "6": "2015-02-19",
                "7": "2015-02-26",
                "8": "2015-03-05"
            },
            "easter": {
                "1": "2015-04-23",
                "2": "2015-04-30",
                "3": "2015-05-07",
                "4": "2015-05-14",
                "5": "2015-05-21",
                "6": "2015-05-28",
                "7": "2015-06-04",
                "8": "2015-06-11"
            }
        },
        "2015": {
            "michaelmas": {
                "1": "2015-10-08",
                "2": "2015-10-15",
                "3": "2015-10-22",
                "4": "2015-10-29",
                "5": "2015-11-05",
                "6": "2015-11-12",
                "7": "2015-11-19",
                "8": "2015-11-26"
            },
            "lent": {
                "1": "2016-01-14",
                "2": "2016-01-21",
                "3": "2016-01-28",
                "4": "2016-02-04",
                "5": "2016-02-11",
                "6": "2016-02-18",
                "7": "2016-02-25",
                "8": "2016-03-03"
            },
            "easter": {
                "1": "2016-04-21",
                "2": "2016-04-28",
                "3": "2016-05-05",
                "4": "2016-05-12",
                "5": "2016-05-19",
                "6": "2016-05-26",
                "7": "2016-06-02",
                "8": "2016-06-09"
            }
        },
        "2016": {
            "michaelmas": {
                "1": "2016-10-06",
                "2": "2016-10-13",
                "3": "2016-10-20",
                "4": "2016-10-27",
                "5": "2016-11-03",
                "6": "2016-11-10",
                "7": "2016-11-17",
                "8": "2016-11-24"
            },
            "lent": {
                "1": "2017-01-19",
                "2": "2017-01-26",
                "3": "2017-02-02",
                "4": "2017-02-09",
                "5": "2017-02-16",
                "6": "2017-02-23",
                "7": "2017-03-02",
                "8": "2017-03-09"
            },
            "easter": {
                "1": "2017-04-27",
                "2": "2017-05-04",
                "3": "2017-05-11",
                "4": "2017-05-18",
                "5": "2017-05-25",
                "6": "2017-06-01",
                "7": "2017-06-08",
                "8": "2017-06-15"
            }
        },
        "2017": {
            "michaelmas": {
                "1": "2017-10-05",
                "2": "2017-10-12",
                "3": "2017-10-19",
                "4": "2017-10-26",
                "5": "2017-11-02",
                "6": "2017-11-09",
                "7": "2017-11-16",
                "8": "2017-11-23"
            },
            "lent": {
                "1": "2018-01-18",
                "2": "2018-01-25",
                "3": "2018-02-01",
                "4": "2018-02-08",
                "5": "2018-02-15",
                "6": "2018-02-22",
                "7": "2018-03-01",
                "8": "2018-03-08"
            },
            "easter": {
                "1": "2018-04-26",
                "2": "2018-05-03",
                "3": "2018-05-10",
                "4": "2018-05-17",
                "5": "2018-05-24",
                "6": "2018-05-31",
                "7": "2018-06-07",
                "8": "2018-06-14"
            }
        },
        "2018": {
            "michaelmas": {
                "1": "2018-10-04",
                "2": "2018-10-11",
                "3": "2018-10-18",
                "4": "2018-10-25",
                "5": "2018-11-01",
                "6": "2018-11-08",
                "7": "2018-11-15",
                "8": "2018-11-22"
            },
            "lent": {
                "1": "2019-01-17",
                "2": "2019-01-24",
                "3": "2019-01-31",
                "4": "2019-02-07",
                "5": "2019-02-14",
                "6": "2019-02-21",
                "7": "2019-02-28",
                "8": "2019-03-07"
            },
            "easter": {
                "1": "2019-04-25",
                "2": "2019-05-02",
                "3": "2019-05-09",
                "4": "2019-05-16",
                "5": "2019-05-23",
                "6": "2019-05-30",
                "7": "2019-06-06",
                "8": "2019-06-13"
            }
        },
        "2019": {
            "michaelmas": {
                "1": "2019-10-10",
                "2": "2019-10-17",
                "3": "2019-10-24",
                "4": "2019-10-31",
                "5": "2019-11-07",
                "6": "2019-11-14",
                "7": "2019-11-21",
                "8": "2019-11-28"
            },
            "lent": {
                "1": "2020-01-16",
                "2": "2020-01-23",
                "3": "2020-01-30",
                "4": "2020-02-06",
                "5": "2020-02-13",
                "6": "2020-02-20",
                "7": "2020-02-27",
                "8": "2020-03-05"
            },
            "easter": {
                "1": "2020-04-23",
                "2": "2020-04-30",
                "3": "2020-05-07",
                "4": "2020-05-14",
                "5": "2020-05-21",
                "6": "2020-05-28",
                "7": "2020-06-04",
                "8": "2020-06-11"
            }
        },
        "2020": {
            "michaelmas": {
                "1": "2020-10-08",
                "2": "2020-10-15",
                "3": "2020-10-22",
                "4": "2020-10-29",
                "5": "2020-11-05",
                "6": "2020-11-12",
                "7": "2020-11-19",
                "8": "2020-11-26"
            },
            "lent": {
                "1": "2021-01-21",
                "2": "2021-01-28",
                "3": "2021-02-04",
                "4": "2021-02-11",
                "5": "2021-02-18",
                "6": "2021-02-25",
                "7": "2021-03-04",
                "8": "2021-03-11"
            },
            "easter": {
                "1": "2021-04-29",
                "2": "2021-05-06",
                "3": "2021-05-13",
                "4": "2021-05-20",
                "5": "2021-05-27",
                "6": "2021-06-03",
                "7": "2021-06-10",
                "8": "2021-06-17"
            }
        },
        "2021": {
            "michaelmas": {
                "1": "2021-10-07",
                "2": "2021-10-14",
                "3": "2021-10-21",
                "4": "2021-10-28",
                "5": "2021-11-04",
                "6": "2021-11-11",
                "7": "2021-11-18",
                "8": "2021-11-25"
            },
            "lent": {
                "1": "2022-01-20",
                "2": "2022-01-27",
                "3": "2022-02-03",
                "4": "2022-02-10",
                "5": "2022-02-17",
                "6": "2022-02-24",
                "7": "2022-03-03",
                "8": "2022-03-10"
            },
            "easter": {
                "1": "2022-04-28",
                "2": "2022-05-05",
                "3": "2022-05-12",
                "4": "2022-05-19",
                "5": "2022-05-26",
                "6": "2022-06-02",
                "7": "2022-06-09",
                "8": "2022-06-16"
            }
        },
        "2022": {
            "michaelmas": {
                "1": "2022-10-06",
                "2": "2022-10-13",
                "3": "2022-10-20",
                "4": "2022-10-27",
                "5": "2022-11-03",
                "6": "2022-11-10",
                "7": "2022-11-17",
                "8": "2022-11-24"
            },
            "lent": {
                "1": "2023-01-19",
                "2": "2023-01-26",
                "3": "2023-02-02",
                "4": "2023-02-09",
                "5": "2023-02-16",
                "6": "2023-02-23",
                "7": "2023-03-02",
                "8": "2023-03-09"
            },
            "easter": {
                "1": "2023-04-27",
                "2": "2023-05-04",
                "3": "2023-05-11",
                "4": "2023-05-18",
                "5": "2023-05-25",
                "6": "2023-06-01",
                "7": "2023-06-08",
                "8": "2023-06-15"
            }
        },
        "2023": {
            "michaelmas": {
                "1": "2023-10-05",
                "2": "2023-10-12",
                "3": "2023-10-19",
                "4": "2023-10-26",
                "5": "2023-11-02",
                "6": "2023-11-09",
                "7": "2023-11-16",
                "8": "2023-11-23"
            },
            "lent": {
                "1": "2024-01-18",
                "2": "2024-01-25",
                "3": "2024-02-01",
                "4": "2024-02-08",
                "5": "2024-02-15",
                "6": "2024-02-22",
                "7": "2024-02-29",
                "8": "2024-03-07"
            },
            "easter": {
                "1": "2024-04-25",
                "2": "2024-05-02",
                "3": "2024-05-09",
                "4": "2024-05-16",
                "5": "2024-05-23",
                "6": "2024-05-30",
                "7": "2024-06-06",
                "8": "2024-06-13"
            }
        },
        "2024": {
            "michaelmas": {
                "1": "2024-10-10",
                "2": "2024-10-17",
                "3": "2024-10-24",
                "4": "2024-10-31",
                "5": "2024-11-07",
                "6": "2024-11-14",
                "7": "2024-11-21",
                "8": "2024-11-28"
            },
            "lent": {
                "1": "2025-01-23",
                "2": "2025-01-30",
                "3": "2025-02-06",
                "4": "2025-02-13",
                "5": "2025-02-20",
                "6": "2025-02-27",
                "7": "2025-03-06",
                "8": "2025-03-13"
            },
            "easter": {
                "1": "2025-05-01",
                "2": "2025-05-08",
                "3": "2025-05-15",
                "4": "2025-05-22",
                "5": "2025-05-29",
                "6": "2025-06-05",
                "7": "2025-06-12",
                "8": "2025-06-19"
            }
        },
        "2025": {
            "michaelmas": {
                "1": "2025-10-09",
                "2": "2025-10-16",
                "3": "2025-10-23",
                "4": "2025-10-30",
                "5": "2025-11-06",
                "6": "2025-11-13",
                "7": "2025-11-20",
                "8": "2025-11-27"
            },
            "lent": {
                "1": "2026-01-22",
                "2": "2026-01-29",
                "3": "2026-02-05",
                "4": "2026-02-12",
                "5": "2026-02-19",
                "6": "2026-02-26",
                "7": "2026-03-05",
                "8": "2026-03-12"
            },
            "easter": {
                "1": "2026-04-30",
                "2": "2026-05-07",
                "3": "2026-05-14",
                "4": "2026-05-21",
                "5": "2026-05-28",
                "6": "2026-06-04",
                "7": "2026-06-11",
                "8": "2026-06-18"
            }
        },
        "2026": {
            "michaelmas": {
                "1": "2026-10-08",
                "2": "2026-10-15",
                "3": "2026-10-22",
                "4": "2026-10-29",
                "5": "2026-11-05",
                "6": "2026-11-12",
                "7": "2026-11-19",
                "8": "2026-11-26"
            },
            "lent": {
                "1": "2027-01-21",
                "2": "2027-01-28",
                "3": "2027-02-04",
                "4": "2027-02-11",
                "5": "2027-02-18",
                "6": "2027-02-25",
                "7": "2027-03-04",
                "8": "2027-03-11"
            },
            "easter": {
                "1": "2027-04-29",
                "2": "2027-05-06",
                "3": "2027-05-13",
                "4": "2027-05-20",
                "5": "2027-05-27",
                "6": "2027-06-03",
                "7": "2027-06-10",
                "8": "2027-06-17"
            }
        },
        "2027": {
            "michaelmas": {
                "1": "2027-10-07",
                "2": "2027-10-14",
                "3": "2027-10-21",
                "4": "2027-10-28",
                "5": "2027-11-04",
                "6": "2027-11-11",
                "7": "2027-11-18",
                "8": "2027-11-25"
            },
            "lent": {
                "1": "2028-01-20",
                "2": "2028-01-27",
                "3": "2028-02-03",
                "4": "2028-02-10",
                "5": "2028-02-17",
                "6": "2028-02-24",
                "7": "2028-03-02",
                "8": "2028-03-09"
            },
            "easter": {
                "1": "2028-04-27",
                "2": "2028-05-04",
                "3": "2028-05-11",
                "4": "2028-05-18",
                "5": "2028-05-25",
                "6": "2028-06-01",
                "7": "2028-06-08",
                "8": "2028-06-15"
            }
        },
        "2028": {
            "michaelmas": {
                "1": "2028-10-05",
                "2": "2028-10-12",
                "3": "2028-10-19",
                "4": "2028-10-26",
                "5": "2028-11-02",
                "6": "2028-11-09",
                "7": "2028-11-16",
                "8": "2028-11-23"
            },
            "lent": {
                "1": "2029-01-18",
                "2": "2029-01-25",
                "3": "2029-02-01",
                "4": "2029-02-08",
                "5": "2029-02-15",
                "6": "2029-02-22",
                "7": "2029-03-01",
                "8": "2029-03-08"
            },
            "easter": {
                "1": "2029-04-26",
                "2": "2029-05-03",
                "3": "2029-05-10",
                "4": "2029-05-17",
                "5": "2029-05-24",
                "6": "2029-05-31",
                "7": "2029-06-07",
                "8": "2029-06-14"
            }
        },
        "2029": {
            "michaelmas": {
                "1": "2029-10-04",
                "2": "2029-10-11",
                "3": "2029-10-18",
                "4": "2029-10-25",
                "5": "2029-11-01",
                "6": "2029-11-08",
                "7": "2029-11-15",
                "8": "2029-11-22"
            },
            "lent": {
                "1": "2030-01-17",
                "2": "2030-01-24",
                "3": "2030-01-31",
                "4": "2030-02-07",
                "5": "2030-02-14",
                "6": "2030-02-21",
                "7": "2030-02-28",
                "8": "2030-03-07"
            },
            "easter": {
                "1": "2030-04-25",
                "2": "2030-05-02",
                "3": "2030-05-09",
                "4": "2030-05-16",
                "5": "2030-05-23",
                "6": "2030-05-30",
                "7": "2030-06-06",
                "8": "2030-06-13"
            }
        }
    };

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

            this.weekSpinner = new Calendar.DateSpinner({
                el: ".js-date-spinner.js-agendaWeek",
                type: "week",
                calendar: this.fullCalendarView,
                terms: terms
            }),

            this.termSpinner = new Calendar.DateSpinner({
                el: ".js-date-spinner.js-term",
                type: "term",
                calendar: this.fullCalendarView,
                terms: terms
            });

            this.monthSpinner = new Calendar.DateSpinner({
                el: ".js-date-spinner.js-month",
                type: "month",
                calendar: this.fullCalendarView,
                terms: terms
            });

            this.calendarSpinners = [
                this.weekSpinner,
                this.termSpinner,
                this.monthSpinner
            ];

            Backbone.history.start();

            this.modulesSelector.on("partChanged", this.partChangedHandler);
            this.calendarViewNavigation.on("viewChanged", this.viewChangedHandler);
            this.modulesList.on("timetableUpdated", this.timetableUpdatedHandler);

            this.weekSpinner.on("change", _.bind(this.renderSpinners, this, this.weekSpinner));
            this.termSpinner.on("change", _.bind(this.renderSpinners, this, this.termSpinner));
            this.monthSpinner.on("change", _.bind(this.renderSpinners, this, this.monthSpinner));

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
