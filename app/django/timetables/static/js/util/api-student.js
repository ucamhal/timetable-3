define([
    "jquery",
    "underscore",
    "util/api"
], function ($, _, api) {
    "use strict";

    var doAjax = api.doAjax;

    // Student specific api functions
    var addToTimetable = function addToTimetable(userPath, fullpath, eventsourceId, eventId, crsfToken, callback) {
        var url =  "/" + userPath + ".link",
            type = "post",
            data = {
                t: fullpath,
                es: eventsourceId,
                e: eventId,
                csrfmiddlewaretoken: crsfToken
            };
        doAjax(url, type, data, callback);
    };

    var removeFromTimetable = function removeFromTimetable(userPath, fullpath, eventsourceId, eventId, crsfToken, callback) {
        var url = "/" + userPath + ".link",
            type = "post",
            data = {
                td: fullpath,
                esd: eventsourceId,
                ed: eventId,
                csrfmiddlewaretoken: crsfToken
            };
        doAjax(url, type, data, callback);
    };

    var getModulesList = function getModulesList(fullpath, userPath, callback) {
        var url = "/" + fullpath + ".children.html",
            type = "get",
            data = {
                t: userPath
            };
        doAjax(url, type, data, callback);
    };

    var getUserEventsList = function getUserEventsList(userPath, year, month, callback) {
        var url = "/" + userPath + ".callist.html",
            type = "get",
            data = {
                y: year,
                m: month
            };
        doAjax(url, type, data, callback);
    };

    var resetUserFeed = function resetUserFeed(userPath, callback) {
        var url = "/" + userPath + ".resetfeed",
            type = "post";
        doAjax(url, type, undefined, callback);
    };

    return _.extend(api, {
        addToTimetable: addToTimetable,
        removeFromTimetable: removeFromTimetable,
        getModulesList: getModulesList,
        getUserEventsList: getUserEventsList,
        resetUserFeed: resetUserFeed
    });
});
