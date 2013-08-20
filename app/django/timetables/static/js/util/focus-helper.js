define([
    "jquery",
    "underscore"
], function ($, _) {
    "use strict";

    // This file exists so that we can keep the weird IE8 focus hacks in one
    // place.
    return {
        isIE: function () {
            if (this._isIE === undefined) {
                this._isIE = ($.browser.msie !== undefined);
            }
            return this._isIE;
        },
        isIE8: function () {
            if (this._isIE8 === undefined) {
                this._isIE8 = (this.isIE() === true && $.browser.version === "8.0");
            }
            return this._isIE8;
        },
        focusTo: function ($to, evilThingsNotAllowed) {
            // Provide the ability to disable ie8 hacks by setting
            // "evilThingsNotAllowed" to true since it's not always necessary
            // to do this.
            if (!evilThingsNotAllowed && this.isIE8() === true) {
                // If we don't defer the focus, in a lot of cases IE8 would put
                // the focus on the element but whenever something renders on
                // the page as a direct result of the focus change it removes
                // the focus again.

                // Defer is the same as setting an empty timeout: It waits until
                // the current call stack has cleared before executing the
                // suppled function.

                // This improves focussing in IE8, but it doesn't completely fix
                // it. More work is needed to make pages keyboard accessible to
                // users using IE8.
                _.defer(function () {
                    // It also seems to like it if we blur the current focussed
                    // element before putting the focus on something else.
                    $(document.activeElement).blur();
                    _.defer(function () {
                        $to.focus();
                    });
                });
            } else {
                // Standard behavior
                $to.focus();
            }
        }
    };
});
