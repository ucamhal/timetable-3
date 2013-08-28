define([
    "jquery"
], function ($) {
    "use strict";

    // This file contains common api functions used by both the student and the
    // admin code.

    var doAjax = function doAjax(url, type, data, callback, global) {
        $.ajax({
            url: url,
            type: type,
            data: data,
            global: global,
            success: function (response) {
                callback(null, response);
            },
            error: function (jqXHR) {
                callback({
                    code: jqXHR.status,
                    msg: jqXHR.responseText || jqXHR.statusText
                });
            }
        });
    };

    var checkCanaryStillAlive = function checkCanaryStillAlive(callback) {
        var url = "/canary",
            type = "get",
            // This is to prevent the global error handler being fired when the
            // request fails. Else it would result in an infinite loop.
            global = false;
        doAjax(url, type, undefined, callback, global);
    };

    var getSeriesSubject = function getSeriesSubject(seriesId, callback) {
        var url = "/series/" + encodeURIComponent(seriesId) + "/subject",
            type = "get";
        doAjax(url, type, undefined, callback);
    };

    return {
        doAjax: doAjax,
        checkCanaryStillAlive: checkCanaryStillAlive,
        getSeriesSubject: getSeriesSubject
    };
});
