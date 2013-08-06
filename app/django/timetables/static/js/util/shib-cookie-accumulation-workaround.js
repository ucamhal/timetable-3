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
            + "=; expires=" + new Date(0) + "; path=/";
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
