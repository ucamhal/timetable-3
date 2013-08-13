define([
    "underscore",
    "jquery-jeditable",
    "jquery-autosize"
], function (_, $) {
    "use strict";

    $.editable.addInputType("tablecell", _.extend(_.clone($.editable.types.textarea), {
        plugin: function (settings) {
            var $textarea = $("textarea", this);
            // Enable autogrow + add maxlength support
            $textarea.attr("maxlength", settings.maxLength).autosize(settings.autosize);
            $(this).parents(".js-field").addClass("being-edited").removeAttr("tabindex");
        }
    }));

    $.editable.addInputType("type-select", _.extend(_.clone($.editable.types.select), {
        plugin: function () {
            $(this).parents(".js-field").addClass("being-edited").removeAttr("tabindex");
        }
    }));

    $.editable.addInputType("title", _.extend(_.clone($.editable.types.text), {
        plugin: function (settings) {
            $("input", this).attr("maxlength", settings.maxLength);
            $(this).parents(".js-value").addClass("being-edited");
        }
    }));
});
