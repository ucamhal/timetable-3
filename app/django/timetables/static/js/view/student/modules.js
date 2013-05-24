define([
    "jquery",
    "underscore",
    "backbone"
], function ($, _, Backbone) {
    "use strict";

    var ModulesList = Backbone.View.extend({
        initialize: function (opts) {
            if (opts.thingPath) {
                this.thingPath = opts.thingPath;
            } else {
                throw new Error("Please provide a thingpath for the modules list to work.");
            }

            if (opts.crsfToken) {
                this.crsfToken = opts.crsfToken;
            } else {
                throw new Error("Please provide a crsfToken for modules list to work.");
            }

            _.bindAll(this, "updateList");
        },

        events: {
            "click a.js-more" : "moreClickHandler",
            "click a.js-less" : "lessClickHandler",
            "click a.js-btn-add, a.js-btn-remove" : "moduleButtonClickHandler"
        },

        associate: function ($source, add) {
            var self = this;
            var sourcepath = this.thingPath;
            var crsf = this.crsfToken;
            var postdata = {};
            if ( add ) {
                postdata.t = $source.attr("data-fullpath");
                postdata.es = $source.attr("data-eventsourceid");
                postdata.e = $source.attr("data-eventid");
            } else {
                postdata.td = $source.attr("data-fullpath");
                postdata.esd = $source.attr("data-eventsourceid");
                postdata.ed = $source.attr("data-eventid");
            }
            postdata.csrfmiddlewaretoken = crsf;
            $.post(sourcepath+".link", postdata, function() {
                self.updateButtonStates($source);
                _.dispatchEvent(self, "timetableUpdated");
            }).error(function(response, status, error) {
                console.log("Status code is "+response.status+" error:"+error);
                if ( response.status === 403 ) {
                    $("#signinModal").modal("show");
                } else {
                    $("#errorModal").modal("show");
                }
            });
        },

        updateButtonStates: function ($source) {
            if ($source.is(".js-btn-module-level")) {
                this.toggleButtonState($source.parent().parent().find("a.btn"), $source.is(".js-btn-add"));
            } else {
                this.toggleButtonState($source, $source.is(".js-btn-add"));
                if ($source.parent().parent().is(".courseMoreInfo")) {
                    if ($source.parent().parent().find(".js-btn-add").length <= 0) {
                        this.toggleButtonState($source.parent().parent().parent().find(".js-btn-add.js-btn-module-level"), true);
                    } else {
                        this.toggleButtonState($source.parent().parent().parent().find(".js-btn-remove.js-btn-module-level"), false);
                    }
                }
            }
        },

        toggleButtonState: function ($btn, fromAdd) {
            if (fromAdd === true) {
                $btn.removeClass("js-btn-add btn-success").addClass("js-btn-remove btn-danger").text("Remove");
            } else {
                $btn.removeClass("js-btn-remove btn-danger").addClass("js-btn-add btn-success").text("Add");
            }
        },

        moduleButtonClickHandler: function (event) {
            var $target = $(event.currentTarget);

            if ($target.is(".js-btn-module-level")) {
                this.associate($target.parent().parent().find("a.btn"), $target.is(".js-btn-add"));
            } else {
                this.associate($target, $target.is(".js-btn-add"));
            }

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
        },

        setHeight: function (height) {
            this.$el.height(height);
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

        moduleChangedHandler: function () {
            var selectedOption = this.$moduleSelect.find("option:selected");
            this.renderPartsSelect(selectedOption.data("levels"));
            this.partChangedHandler();
        },

        partChangedHandler: function () {
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

    var ListView = Backbone.View.extend({
        initialize: function (opts) {
            if (!opts.thingPath) {
                throw new Error("ListView needs a thingpath to work correctly");
            } else {
                this.thingPath = opts.thingPath;
            }
        },

        setActiveDate: function (activeDate) {
            if (this.activeDate !== activeDate) {
                this.activeDate = activeDate;
                this.render();
            }
        },

        show: function () {
            this.$el.show();
        },

        hide: function () {
            this.$el.hide();
        },

        render: function () {
            var self = this;

            $.ajax({
                url: self.thingPath + ".callist.html",
                type: "GET",
                data: {
                    "y": self.activeDate.getFullYear(),
                    "m" : self.activeDate.getMonth() + 1
                },
                success: function (response) {
                    self.$el.empty().append(response);
                },
                error: function () {
                    console.log("list view data not fetched");
                    console.log(arguments);
                }
            });
        }
    });

    return {
        ModulesList: ModulesList,
        ModulesSelector: ModulesSelector,
        ListView: ListView
    };
});
