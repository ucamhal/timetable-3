define(["jquery", "underscore", "rangy-core", "util/assert"], function($, _, rangy, assert) {
    "use strict";

    // Ensure rangy is initiatlised
    rangy.init();

    /**
     * A paste event handler for contenteditable=true elements which need to
     * maintain plain text.
     *
     * When a paste event occurs the user's selection/caret location is saved
     * and the caret is restored to this position after the pasted text/elements
     * have been converted to plaintext.
     */
    function maintainPlainText(pasteEvent) {
        var $this = $(pasteEvent.target),
            selection = rangy.getSelection(),
            range,
            rangeRightOffset,
            textNodes,
            node,
            newRightOffset;

        var TEXT_NODE = 3;

        assert(selection.rangeCount === 1);

        // Get the current cursor position
        range = selection.getRangeAt(0);
        assert(range.endContainer.nodeType === TEXT_NODE);

        // We need the offset from the right side of the textnode
        rangeRightOffset = range.endContainer.length - range.endOffset;

        // Defer to allow the browser to paste in the content
        _.defer(function() {
            // Strip any html elements
            $this.text($this.text());

            // Put the user's cursor back where it was...
            // Find the current text node in our editable element
            textNodes = $this.contents().filter(function() {
                return this.nodeType === TEXT_NODE;
            });
            assert(textNodes.length === 1); // Should be len 1 seeing as we just called .text(value)
            node = textNodes[0];

            // Calculate the new offset (from the left) given the current contents
            newRightOffset = node.length - rangeRightOffset;
            range.setStart(node, newRightOffset);
            range.setEnd(node, newRightOffset);

            // Move the cursor to our range
            selection.setSingleRange(range);
        });
    }

    /**
     * Watch for paste events on contenteditable=true elements and call
     * maintainPlainText() for each event.
     */
    function alwaysMaintainPlainText() {
        $(document).on("paste", "[contenteditable=true]", maintainPlainText);
    }

    return {
        maintainPlainText: maintainPlainText,
        alwaysMaintainPlainText: alwaysMaintainPlainText
    };
});
