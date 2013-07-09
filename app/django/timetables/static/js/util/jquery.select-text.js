define([
    "jquery"
], function ($) {
    "use strict";

    $.fn.selectText = function selectText() {
        var $this = $(this),
            element,
            range,
            selection;

        if ($this.length) {
            element = $this[0];

            if (document.body.createTextRange) {
                range = document.body.createTextRange();
                range.moveToElementText(element);
                range.select();
            } else if (window.getSelection) {
                selection = window.getSelection();
                range = document.createRange();
                range.selectNodeContents(element);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }

        return $this;
    };

    return $;
});
