define([
    "jquery"
], function ($) {
    "use strict";

    var doAjax = function doAjax(url, type, data, callback) {
        $.ajax({
            url: url,
            type: type,
            data: data,
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

    var addThingLink = function addThingLink(thingFullpath, linkFullpath, callback) {
        var url = "/" + encodeURIComponent(thingFullpath) + "/links/new",
            type = "post",
            data = {
                fullpath: linkFullpath
            };
        doAjax(url, type, data, callback);
    };

    var removeThingLink = function removeThingLink(thingFullpath, linkFullpath, callback) {
        var url = "/" + encodeURIComponent(thingFullpath) + "/links/delete",
            type = "post",
            data = {
                fullpath: linkFullpath
            };
        doAjax(url, type, data, callback);
    };

    return {
        addThingLink: addThingLink,
        removeThingLink: removeThingLink
    };
});
