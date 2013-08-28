define([
    "jquery",
    "underscore",
    "util/api"
], function ($, _, api) {
    "use strict";

    var doAjax = api.doAjax;

    // Admin specific api functions.
    // Links
    var addThingLink = function addThingLink(thingFullpath, linkFullpath, callback) {
        var url = "/" + thingFullpath + "/links/new",
            type = "post",
            data = {
                fullpath: linkFullpath
            };
        doAjax(url, type, data, callback);
    };

    var removeThingLink = function removeThingLink(thingFullpath, linkFullpath, callback) {
        var url = "/" + thingFullpath + "/links/delete",
            type = "post",
            data = {
                fullpath: linkFullpath
            };
        doAjax(url, type, data, callback);
    };

    // Series
    var getEvents = function getEvents(seriesId, writeable, callback) {
        var url = "/series/" + encodeURIComponent(seriesId) + "/list-events",
            type = "get",
            data = {
                writeable: writeable
            };
        doAjax(url, type, data, callback);
    };

    var saveEvents = function saveEvents(seriesId, eventsData, callback) {
        var url = "/series/" + encodeURIComponent(seriesId) + "/edit",
            type = "post";
        doAjax(url, type, eventsData, callback);
    };

    var deleteSeries = function deleteSeries(seriesId, callback) {
        var url = "/series/" + encodeURIComponent(seriesId) + "/delete",
            type = "post";
        doAjax(url, type, undefined, callback);
    };

    // Modules
    var deleteModule = function deleteModule(moduleId, callback) {
        var url = "/things/" + encodeURIComponent(moduleId) + "/delete",
            type = "post";
        doAjax(url, type, undefined, callback);
    };

    // Lock
    var getTimetablesLockStatuses = function getTimetablesLockStatus(timetables, callback) {
        var url = "/locks/status",
            type = "post";
        doAjax(url, type, timetables, callback);
    };

    var refreshLock = function refreshLock(fullpath, editing, callback) {
        var url = "/" + fullpath + ".refresh-lock",
            type = "post",
            data = {
                editing: editing
            };
        doAjax(url, type, data, callback);
    };

    return _.extend(api, {
        addThingLink: addThingLink,
        removeThingLink: removeThingLink,
        getEvents: getEvents,
        saveEvents: saveEvents,
        deleteSeries: deleteSeries,
        deleteModule: deleteModule,
        getTimetablesLockStatuses: getTimetablesLockStatuses,
        refreshLock: refreshLock
    });
});
