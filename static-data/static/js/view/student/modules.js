define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {

    var ModulesList = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, "updateList");
        },

        events: {
            "click a.js-more" : "moreClickHandler",
            "click a.js-less" : "lessClickHandler",

            "click a.js-btn-add" : "addClickHandler",
            "click a.js-btn-remove" : "removeClickHandler"
        },

        removeClickHandler: function (event) {
            var $target = $(event.target),
                $source = $target,
                onModuleLevel = $source.hasClass("js-btn-module-level");

            if (onModuleLevel) {
                $source = $target.parent().parent().find("a.btn");
            }

            this.updatePersonalTimetable({
                td: $source.data("fullpath"),
                esd: $source.data("eventsourceid"),
                ed: $source.data("eventid")
            }, _.bind(this.updateButtonStates, this, $source, false, onModuleLevel));

            event.preventDefault();
        },

        updateButtonStates: function () {

        },

        addClickHandler: function (event) {
            var $target = $(event.target),
                $source = $target
                onModuleLevel = $source.hasClass("js-btn-module-level");

            if (onModuleLevel) {
                $source = $target.parent().parent().find("a.btn");
            }

            this.updatePersonalTimetable({
                t: $source.data("fullpath"),
                es: $source.data("eventsourceid"),
                e: $source.data("eventid")
            }, _.bind(this.updateButtonStates, this, $source, true, onModuleLevel));

            event.preventDefault();
        },

        updatePersonalTimetable: function (postData, callback) {
            //implement callback
            var self = this;
            console.log("postData", postData);
            postData.crsfmiddlewatetoken = this.getCrsfToken();

            $.ajax({
                type: "POST",
                data: postData,
                url: self.getThingPath() + ".link",
                success: function () {
                    if (typeof callback === "function") {
                        callback.call();
                    }

                    console.log("Timetable update success:", arguments);
                },
                error: function () {
                    if (typeof callback === "function") {
                        callback.call();
                    }

                    console.log("Timetable update error:", arguments);
                }
            });
        },

        lessClickHandler: function (event) {
            var $target = $(event.currentTarget);

            $target.removeClass("js-less").addClass("js-more");
            $target.text("more");

            $(".courseMoreInfo", $target.parent().parent()).stop().slideUp("fast");

            event.preventDefault();
        },

        moreClickHandler: function (event) {
            var $target = $(event.currentTarget);
            
            $target.removeClass("js-more").addClass("js-less");
            $target.text("show less");

            $(".courseMoreInfo", $target.parent().parent()).stop().hide().slideDown("fast");

            event.preventDefault();
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

        getCrsfToken: function () {
            if (!this.crsfToken) {
                if ($("#userinfo").length === 1) {
                    this.crsfToken = $("#userinfo").find("[name=crsfmiddlewatetoken]").val();
                } else if ($("#thinginfo").length === 1) {
                    this.crsfToken = $("#thinginfo").find("[name=crsfmiddlewatetoken]").val();
                }
            }

            return this.crsfToken;
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
