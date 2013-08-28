define([
    "jquery",
    "underscore",
    "backbone",
    "view/calendar",
    "view/date-spinner",
    "model/calendarModel",
    "bootstrap",
    "fullcalendar"
], function($, _, Backbone, FullCalendarView, DateSpinner, CalendarModel) {
    "use strict";

    var TimetableCalendar = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this);

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

            this.calendar = new FullCalendarView({
                el: $(".js-calendar"),
                defaultView: "agendaWeek",
                firstDay: 4,
                eventsFeed: $(".js-calendar").data("events-url")
            });

            this.weekSpinner = new DateSpinner({
                el: ".js-date-spinner.js-week"
            });

            this.termSpinner = new DateSpinner({
                el: ".js-date-spinner.js-term"
            });

            this.bindEvents();

            this.calendarModel.setActiveDate(new Date());
        },

        bindEvents: function () {
            this.listenTo(this.weekSpinner, "prev", this.onWeekPrev);
            this.listenTo(this.weekSpinner, "next", this.onWeekNext);

            this.listenTo(this.termSpinner, "prev", this.onTermPrev);
            this.listenTo(this.termSpinner, "next", this.onTermNext);

            this.listenTo(this.calendarModel, "change:activeDate", this.onActiveDateChange);
            this.listenTo(this.calendarModel, "change:activeTerm", this.onActiveTermChange);
            this.listenTo(this.calendarModel, "change:activeWeek", this.onActiveWeekChange);

            $(window).on("resize", this.resize);
        },

        onActiveDateChange: function (model, date) {
            this.calendar.goToDate(date);
            this.updateWeekSpinnerButtonStates();
            this.updateTermSpinnerButtonStates();
        },

        onActiveTermChange: function (model) {
            this.termSpinner.set({
                value: model.getActiveTermName() || "Outside term"
            });
        },

        onActiveWeekChange: function (model, activeWeek) {
            this.weekSpinner.set({
                value: activeWeek ? "Week " + activeWeek : "Outside term"
            });

            this.updateWeekSpinnerButtonStates();
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

        onTermPrev: function () {
            this.calendarModel.goToPrevTerm();
        },

        onTermNext: function () {
            this.calendarModel.goToNextTerm();
        },

        updateTermSpinnerButtonStates: function () {
            var model = this.calendarModel;
            this.termSpinner.set({
                prev: model.getPrevTermForDate(model.getActiveDate()),
                next: model.getNextTermForDate(model.getActiveDate())
            });
        },

        resize: function () {
            if (this.calendar.eventPopup) {
                this.calendar.eventPopup.updatePosition();
            }
        }
    });

    return new TimetableCalendar();
});
