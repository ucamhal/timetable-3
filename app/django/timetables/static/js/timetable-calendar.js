define([
    "jquery",
    "underscore",
    "view/admin/calendar",
    "view/cookieHandler",
    "bootstrap",
    "fullcalendar",
    "not-implemented-tooltips"
], function($, _, Calendar, CookieHandler) {
    "use strict";

    var calendar = new Calendar.FullCalendarView({
        el: $(".js-calendar"),
        defaultView: "agendaWeek",
        firstDay: 4,
        eventsFeed: $(".js-calendar").data("events-url")
    });

    $.get("/static/js/data/terms.json", function (terms) {
        var weekSpinner = new Calendar.DateSpinner({
            el: ".js-date-spinner.js-week",
            type: "week",
            calendar: calendar,
            terms: terms
        });

        var termSpinner = new Calendar.DateSpinner({
            el: ".js-date-spinner.js-term",
            type: "term",
            calendar: calendar,
            terms: terms
        });

        weekSpinner.on("change", function () {
            termSpinner.render();
        });

        termSpinner.on("change", function () {
            weekSpinner.render();
        });
    });

    new CookieHandler({
        el: ".js-cookie-alert"
    });

    $(window).resize(function () {
        calendar.eventPopup.updatePosition();
    });

    return undefined;
});
