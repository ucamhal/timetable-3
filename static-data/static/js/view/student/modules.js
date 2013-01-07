define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {

    var ModulesList = Backbone.View.extend({
        initialize: function (opts) {

            console.log("ModulesList init");

            if (opts.thingPath) {
                this.thingPath = opts.thingPath;
            } else {
                throw new Error("Please provide a thingpath for the modules list to work.");
            }

            if (opts.crsfToken) {
                this.crsfToken = opts.crsfToken;
            } else {
                throw new Error("Please provide a crsfToken for modules list to work.")
            }

            _.bindAll(this, "updateList");
        },

        events: {
            "click a.js-more" : "moreClickHandler",
            "click a.js-less" : "lessClickHandler",

            "click a.js-btn-add" : "addClickHandler",
            "click a.js-btn-remove" : "removeClickHandler"
        },

        updateSingleButtonState: function ($btn, add) {
            if (add === true) {
                $btn.removeClass("js-btn-remove btn-danger").addClass("js-btn-add btn-success").text("Add");
            } else {
                $btn.removeClass("js-btn-add btn-success").addClass("js-btn-remove btn-danger").text("Remove");
            }
        },

        updateButtonStates: function ($btn, add, onModuleLevel) {
            var $courseMoreInfo;
            if (onModuleLevel) {
                this.updateSingleButtonState($btn.parent().parent().find("a.btn"), !add);
            } else {
                this.updateSingleButtonState($btn, !add);
                if ($btn.parent().parent().is(".courseMoreInfo")) {
                    $courseMoreInfo = $btn.parent().parent();

                    if ($(".js-btn-add", $courseMoreInfo).length <= 0) {
                        this.updateSingleButtonState($(".js-btn-add.js-btn-module-level", $courseMoreInfo.parent()), false)
                    } else {
                        this.updateSingleButtonState($(".js-btn-remove.js-btn-module-level", $courseMoreInfo.parent()), true);
                    }
                }
            }
        },

        addClickHandler: function (event) {
            var $target = $(event.target),
                $source = $target,
                onModuleLevel = $source.hasClass("js-btn-module-level");

            if (onModuleLevel) {
                $source = $target.parent().parent().find("a.btn");
            }

            this.updatePersonalTimetable({
                t: $source.data("fullpath"),
                es: $source.data("eventsourceid"),
                e: $source.data("eventid")
            }, _.bind(this.updateButtonStates, this, $target, true, onModuleLevel));

            return false;
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

            return false;
        },

        updatePersonalTimetable: function (postData, callback) {
            var self = this;
            postData.crsfmiddlewatetoken = this.crsfToken;

            $.ajax({
                type: "POST",
                data: postData,
                url: self.thingPath + ".link",
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

            this.trigger("timetableUpdated");
        },

        lessClickHandler: function (event) {
            var $target = $(event.currentTarget);

            $target.removeClass("js-less").addClass("js-more");
            $target.text("more");

            //$(".courseMoreInfo", $target.parent().parent()).stop().slideUp("fast");
            $(".courseMoreInfo", $target.parent().parent()).slideUp("fast");

            return false;
        },

        moreClickHandler: function (event) {
            var $target = $(event.currentTarget);
            
            $target.removeClass("js-more").addClass("js-less");
            $target.text("show less");

            //$(".courseMoreInfo", $target.parent().parent()).stop().hide().slideDown("fast");
            $(".courseMoreInfo", $target.parent().parent()).slideDown("fast");

            return false;
        },

        updateList: function (fullpath) {
            var self = this;

            $.ajax({
                url: "/" + fullpath + ".children.html?t=" + encodeURIComponent(self.thingPath),
                type: "GET",
                success: function (data) {
                    var modulesFound = self.$(".js-modules-list").empty().append(data).find("> li").length,
                        modulesFoundText = "Found " + modulesFound + " modules";

                    if (modulesFound === 1) {
                        modulesFoundText = "Found 1 module";
                    }

                    self.updateModulesFoundText(modulesFoundText);
                },
                error: function () {
                    //TODO handle errors in the modules panel
                    console.log(arguments);
                    self.$(".js-modules-list").empty();
                }
            });
        },

        updateModulesFoundText: function (to) {
            this.$(".js-modules-found h3").text(to);
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
