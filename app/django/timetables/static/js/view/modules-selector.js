define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {
    "use strict";

    var ModulesSelector = Backbone.View.extend({
        initialize: function () {
            this.$moduleSelect = this.$(".js-module-select");
            this.$partSelect = this.$(".js-part-select");
        },

        events: {
            "change .js-module-select"  : "moduleChangedHandler",
            "change .js-part-select"    : "partChangedHandler"
        },

        moduleChangedHandler: function () {
            var selectedOption = this.$moduleSelect.find("option:selected");
            this.renderPartsSelect(selectedOption.data("levels"));
            this.partChangedHandler();
        },

        partChangedHandler: function () {
            this.trigger("partChanged", this.getValue());
        },

        renderPartsSelect: function (levels) {
            var i;

            $("option:not(:disabled)", this.$partSelect).remove();

            if (levels) {
                for (i = 0; i < levels.length; i += 1) {
                    this.$partSelect.append(this.htmlForLevel(levels[i]));
                }
            }
        },

        getValue: function () {
            return this.$partSelect.val();
        },

        getSelectedModuleOptionFromFullpath: function (fullpath) {
            return $(_.filter($("option", this.$moduleSelect), function (option) {
                return _.any($(option).data("levels"), function (levelObj) {
                    return levelObj.fullpath === fullpath;
                });
            }));
        },

        getModuleTextFromFullpath: function (fullpath) {
            var $selectedModule = this.getSelectedModuleOptionFromFullpath(fullpath);
            return $selectedModule ? $selectedModule.text() : "";
        },

        getPartTextFromFullpath: function (fullpath) {
            var $selectedModule = this.getSelectedModuleOptionFromFullpath(fullpath),
                selectedPart = _.find($selectedModule.data("levels"), function (levelObj) {
                    return levelObj.fullpath === fullpath;
                });

            return selectedPart !== undefined ? selectedPart.level_name : "";
        },

        setSelectsFromFullpath: function (fullpath) {
            if (!fullpath) {
                this.$moduleSelect.val("");
                this.$partSelect.val("");
                this.moduleChangedHandler();
                return;
            }

            if (this.getValue() !== fullpath) {
                var $selectedOption = this.getSelectedModuleOptionFromFullpath(fullpath);
                this.$moduleSelect.val($selectedOption.val());
                this.renderPartsSelect($selectedOption.data("levels"));
                this.$partSelect.val(fullpath);
            }
        },

        htmlForLevel: function (levelData) {
            var $option = $("<option />");
            $option.attr("value", levelData.fullpath);
            $option.text(levelData.level_name);
            return $option;
        }
    });

    return ModulesSelector;
});
