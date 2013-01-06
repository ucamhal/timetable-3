define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {

    var ModulesList = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, "updateList");
        },

        updateList: function (fullpath) {
            var self = this;

            $.ajax({
                url: "/" + fullpath + ".children.html?t=" + encodeURIComponent(self.getThingPath()),
                type: "GET",
                success: function (data) {
                    self.$("ul").empty().append(data);
                },
                error: function () {
                    console.log(arguments);
                    self.$("ul").empty();
                }
            });
        },

        getThingPath: function () {
            if (!this.thingPath) {
                if ($("#userinfo").length === 1) {
                    this.thingPath = "user/" + $("#userinfo").attr("userid");
                } else if ($("#thinginfo").length === 1) {
                    this.thingPath = $("#thinginfo").attr("fullpath");
                }
            }

            return this.thingPath;
        }
    });

    var ModulesSelector = Backbone.View.extend({
        initialize: function () {
            this.$moduleSelect = this.$(".js-module-select");
            this.$partSelect = this.$(".js-part-select");
        },
        
        events: {
            "change .js-module-select"  : "moduleChangedHandler",
            "change .js-part-select"    : "partChangedHandler"
        },

        moduleChangedHandler: function (event) {
            var selectedOption = this.$moduleSelect.find("option:selected");
            this.renderPartsSelect(selectedOption.data("levels"));
            this.partChangedHandler();
        },

        partChangedHandler: function (event) {
            this.trigger("partChanged", this.$partSelect.val());
        },

        renderPartsSelect: function (levels) {
            var i;

            $("option:not(:disabled)", this.$partSelect).remove();

            for (i = 0; i < levels.length; i += 1) {
                this.$partSelect.append(this.htmlForLevel(levels[i]));
            }
        },

        getSelectedModuleOptionFromFullpath: function (fullpath) {
            return $(_.filter($("option", this.$moduleSelect), function (option) {
                return _.any($(option).data("levels"), function (levelObj) {
                    return levelObj.fullpath === fullpath;
                });
            }));
        },

        setSelectsFromFullpath: function (fullpath) {
            if (this.$partSelect.val() !== fullpath) {
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

    return {
        ModulesList: ModulesList,
        ModulesSelector: ModulesSelector
    };

});
