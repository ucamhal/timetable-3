define([
    "qunit",
    "../../model/calendarModel"
], function (qunit, CalendarModel) {
    "use strict";

    var testCalendarModel = function testCalendarModel() {
        qunit.module("Calendar model functions");

        var michaelmas = {
            "name": "michaelmas",
            "start": new Date(2012, 9, 4)
        };

        var lent = {
            "name": "lent",
            "start": new Date(2013, 0, 17)
        };

        var easter = {
            "name": "easter",
            "start": new Date(2013, 3, 25)
        };

        var dates = [
            {
                date: new Date(2011, 9, 4),
                term: undefined,
                week: undefined,
                next: michaelmas,
                previous: undefined,
                cambridgeWeekStart: new Date(2011, 8, 29),
                nextCambridgeWeek: new Date(2011, 9, 6),
                prevCambridgeWeek: new Date(2011, 8, 22)
            },
            {
                date: new Date(2011, 9, 8),
                term: undefined,
                week: undefined,
                next: michaelmas,
                previous: undefined,
                cambridgeWeekStart: new Date(2011, 9, 6),
                nextCambridgeWeek: new Date(2011, 9, 13),
                prevCambridgeWeek: new Date(2011, 8, 29)
            },
            {
                date: new Date(2011, 9, 9),
                term: undefined,
                week: undefined,
                next: michaelmas,
                previous: undefined,
                cambridgeWeekStart: new Date(2011, 9, 6),
                nextCambridgeWeek: new Date(2011, 9, 13),
                prevCambridgeWeek: new Date(2011, 8, 29)
            },
            {
                date: new Date(2012, 9, 3),
                term: undefined,
                monthTerm: michaelmas,
                week: undefined,
                next: michaelmas,
                previous: undefined,
                cambridgeWeekStart: new Date(2012, 8, 27),
                nextCambridgeWeek: new Date(2012, 9, 4),
                prevCambridgeWeek: new Date(2012, 8, 20)
            },
            {
                date: new Date(2012, 9, 4),
                term: michaelmas,
                monthTerm: michaelmas,
                week: 1,
                next: lent,
                previous: undefined,
                cambridgeWeekStart: new Date(2012, 9, 4),
                nextCambridgeWeek: new Date(2012, 9, 11),
                prevCambridgeWeek: new Date(2012, 8, 27)
            },
            {
                date: new Date(2012, 9, 31),
                term: michaelmas,
                monthTerm: michaelmas,
                week: 4,
                next: lent,
                previous: undefined,
                cambridgeWeekStart: new Date(2012, 9, 25),
                nextCambridgeWeek: new Date(2012, 10, 1),
                prevCambridgeWeek: new Date(2012, 9, 18)
            },
            {
                date: new Date(2012, 10, 28),
                term: michaelmas,
                monthTerm: michaelmas,
                week: 8,
                next: lent,
                previous: undefined,
                cambridgeWeekStart: new Date(2012, 10, 22),
                nextCambridgeWeek: new Date(2012, 10, 29),
                prevCambridgeWeek: new Date(2012, 10, 15)
            },
            {
                date: new Date(2012, 10, 29),
                term: undefined,
                monthTerm: michaelmas,
                week: undefined,
                next: lent,
                previous: michaelmas,
                cambridgeWeekStart: new Date(2012, 10, 29),
                nextCambridgeWeek: new Date(2012, 11, 6),
                prevCambridgeWeek: new Date(2012, 10, 22)
            },
            {
                date: new Date(2013, 0, 17),
                term: lent,
                monthTerm: lent,
                week: 1,
                next: easter,
                previous: michaelmas,
                cambridgeWeekStart: new Date(2013, 0, 17),
                nextCambridgeWeek: new Date(2013, 0, 24),
                prevCambridgeWeek: new Date(2013, 0, 10)
            },
            {
                date: new Date(2013, 1, 20),
                term: lent,
                monthTerm: lent,
                week: 5,
                next: easter,
                previous: michaelmas,
                cambridgeWeekStart: new Date(2013, 1, 14),
                nextCambridgeWeek: new Date(2013, 1, 21),
                prevCambridgeWeek: new Date(2013, 1, 7)
            },
            {
                date: new Date(2013, 2, 13),
                term: lent,
                monthTerm: lent,
                week: 8,
                next: easter,
                previous: michaelmas,
                cambridgeWeekStart: new Date(2013, 2, 7),
                nextCambridgeWeek: new Date(2013, 2, 14),
                prevCambridgeWeek: new Date(2013, 1, 28)
            },
            {
                date: new Date(2013, 2, 14),
                term: undefined,
                monthTerm: lent,
                week: undefined,
                next: easter,
                previous: lent,
                cambridgeWeekStart: new Date(2013, 2, 14),
                nextCambridgeWeek: new Date(2013, 2, 21),
                prevCambridgeWeek: new Date(2013, 2, 7)
            },
            {
                date: new Date(2013, 2, 15),
                term: undefined,
                monthTerm: lent,
                week: undefined,
                next: easter,
                previous: lent,
                cambridgeWeekStart: new Date(2013, 2, 14),
                nextCambridgeWeek: new Date(2013, 2, 21),
                prevCambridgeWeek: new Date(2013, 2, 7)
            },
            {
                date: new Date(2013, 3, 25),
                term: easter,
                monthTerm: easter,
                week: 1,
                next: undefined,
                previous: lent,
                cambridgeWeekStart: new Date(2013, 3, 25),
                nextCambridgeWeek: new Date(2013, 4, 2),
                prevCambridgeWeek: new Date(2013, 3, 18)
            },
            {
                date: new Date(2013, 4, 2),
                term: easter,
                monthTerm: easter,
                week: 2,
                next: undefined,
                previous: lent,
                cambridgeWeekStart: new Date(2013, 4, 2),
                nextCambridgeWeek: new Date(2013, 4, 9),
                prevCambridgeWeek: new Date(2013, 3, 25)
            },
            {
                date: new Date(2013, 5, 19),
                term: easter,
                monthTerm: easter,
                week: 8,
                next: undefined,
                previous: lent,
                cambridgeWeekStart: new Date(2013, 5, 13),
                nextCambridgeWeek: new Date(2013, 5, 20),
                prevCambridgeWeek: new Date(2013, 5, 6)
            },
            {
                date: new Date(2013, 5, 20),
                term: undefined,
                monthTerm: easter,
                week: undefined,
                next: undefined,
                previous: easter,
                cambridgeWeekStart: new Date(2013, 5, 20),
                nextCambridgeWeek: new Date(2013, 5, 27),
                prevCambridgeWeek: new Date(2013, 5, 13)
            },
            {
                date: new Date(2013, 7, 20),
                term: undefined,
                week: undefined,
                next: undefined,
                previous: easter,
                cambridgeWeekStart: new Date(2013, 7, 15),
                nextCambridgeWeek: new Date(2013, 7, 22),
                prevCambridgeWeek: new Date(2013, 7, 8)
            }
        ];

        var model = new CalendarModel({
            terms: [
                michaelmas,
                lent,
                easter
            ],
            start: new Date(2012, 8, 1),
            end: new Date(2013, 7, 31)
        });

        qunit.test("putDateWithinBoundaries", function (assert) {
            var start = new Date(1991, 1, 1);
            assert.deepEqual(model.putDateWithinBoundaries(start), model.get("start"), "Start boundary working");

            var end = new Date(2999, 1, 1);
            assert.deepEqual(model.putDateWithinBoundaries(end), model.get("end"), "End boundary working");
        });

        qunit.test("isDateWithinBoundaries", function (assert) {
            var badDates = [
                    new Date(1970, 1, 1),
                    new Date(1982, 11, 23),
                    new Date(1992, 3, 4),
                    new Date(2102, 5, 29),
                    new Date(2983, 10, 19)
                ],
                goodDates = [
                    new Date(2013, 1, 13),
                    new Date(2012, 11, 23),
                    new Date(2013, 3, 4),
                    new Date(2013, 5, 29),
                    new Date(2012, 10, 19)
                ];

            for (var i = 0; i < badDates.length; i += 1) {
                assert.ok(model.isDateWithinBoundaries(badDates[i]) === false, "Bad date found");
                assert.ok(model.isDateWithinBoundaries(goodDates[i]) === true, "Good date found");
            }
        });

        qunit.test("getMonthStartForDate", function (assert) {
            var dates = [
                new Date(1970, 1, 1),
                new Date(1982, 11, 23),
                new Date(1992, 3, 4),
                new Date(2102, 5, 29),
                new Date(2983, 10, 19)
            ];

            for (var i = 0; i < dates.length; i += 1) {
                var year = dates[i].getFullYear(),
                    month = dates[i].getMonth(),
                    day = dates[i].getDate();
                assert.deepEqual(model.getMonthStartForDate(new Date(year, month, day)), new Date(year, month, 1), "Start of month correct");
            }
        });

        qunit.test("getTermForDate", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.getTermForDate(dates[i].date), dates[i].term, "Finds correct term");
            }
        });

        qunit.test("getTermWeekForDate", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.getTermWeekForDate(dates[i].date), dates[i].week, "Finds correct week number");
            }
        });

        qunit.test("getTermEndDate", function (assert) {
            assert.deepEqual(model.getTermEndDate(michaelmas), new Date(2012, 10, 28), "Michaelmas end date correct");
            assert.deepEqual(model.getTermEndDate(lent), new Date(2013, 2, 13), "Lent end date correct");
            assert.deepEqual(model.getTermEndDate(easter), new Date(2013, 5, 19), "Easter end date correct");
        });

        qunit.test("getMonthForDate", function (assert) {
            assert.deepEqual(model.getMonthForDate(new Date(2012, 1, 1)), "February", "Month found");
            assert.deepEqual(model.getMonthForDate(new Date(2112, 6, 3)), "July", "Month found");
            assert.deepEqual(model.getMonthForDate(new Date(2011, 11, 9)), "December", "Month found");
        });

        qunit.test("getNextTermForDate", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.getNextTermForDate(dates[i].date), dates[i].next, "Finds correct next term");
            }
        });

        qunit.test("getPrevTermForDate", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.getPrevTermForDate(dates[i].date), dates[i].previous, "Finds correct previous term");
            }
        });

        qunit.test("getCambridgeWeekStartForDate", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.getCambridgeWeekStartForDate(dates[i].date), dates[i].cambridgeWeekStart, "Start of cambridge week correct");
            }
        });

        qunit.test("moveDateToNextMonth", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                var date = dates[i].date,
                    nextMonth = new Date(date.getFullYear(), date.getMonth() + 1, 1);
                assert.deepEqual(model.moveDateToNextMonth(date), nextMonth, "Successfully moved to next month");
            }
        });

        qunit.test("moveDateToPrevMonth", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                var date = dates[i].date,
                    prevMonth = new Date(date.getFullYear(), date.getMonth() - 1, 1);
                assert.deepEqual(model.moveDateToPrevMonth(date), prevMonth, "Successfully moved to previous month");
            }
        });

        qunit.test("moveDateToNextCambridgeWeek", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.moveDateToNextCambridgeWeek(dates[i].date), dates[i].nextCambridgeWeek, "Successfully moved to next Cambridge week");
            }
        });

        qunit.test("moveDateToPrevCambridgeWeek", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.moveDateToPrevCambridgeWeek(dates[i].date), dates[i].prevCambridgeWeek, "Successfully moved to previous Cambridge week");
            }
        });

        qunit.test("getTermForMonth", function (assert) {
            for (var i = 0; i < dates.length; i += 1) {
                assert.deepEqual(model.getTermForMonth(dates[i].date), dates[i].monthTerm, "Successfully found term for month");
            }
        });
    };

    return {
        test: testCalendarModel
    };
});
