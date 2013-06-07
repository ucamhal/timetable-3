/* global escape */
/**
 * A module for keeping your website working while using Shibboleth.
 */

define(["jquery"], function($) {
    "use strict";

    function getShibstateCookies() {
        var shibstateCookiePattern = /(?:^|;\s*)(_shibstate_\w+)=/g,
            shibstateCookies = [],
            cookie = document.cookie,
            match;

        while((match = shibstateCookiePattern.exec(cookie)) !== null) {
            shibstateCookies.push(match[1]);
        }

        return shibstateCookies;
    }

    function unsetCookie(name) {
        document.cookie = escape(name)
            + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }

    function removeShibstateCookies() {
        $.each(getShibstateCookies(), function(i, c) { unsetCookie(c); });
    }

    function onAjaxComplete() {
        removeShibstateCookies();
    }

    function removeShibstateCookiesAfterJQueryAjaxRequests() {
        $(document).ajaxComplete(onAjaxComplete);
    }

    function preventShibFromDestroyingMyWebsite() {
        removeShibstateCookies();
        removeShibstateCookiesAfterJQueryAjaxRequests();
    }

    return {
        removeShibstateCookies: removeShibstateCookies,
        preventShibFromDestroyingMyWebsite: preventShibFromDestroyingMyWebsite,
        removeShibstateCookiesAfterJQueryAjaxRequests: removeShibstateCookiesAfterJQueryAjaxRequests
    };
});
