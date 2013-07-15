define([
    "jquery",
    "underscore",
    "backbone",
    "util/underscore-mixins"
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
            "hide" : "onSeriesHide",
            "show" : "onSeriesShow",
            "click a.js-btn-add, a.js-btn-remove" : "moduleButtonClickHandler"
        },

        onSeriesHide: function (event) {
            var $chevron = $(event.target).parent().find(".chevron");
            $chevron.removeClass("icon-chevron-down").addClass("icon-chevron-right");
        },

        onSeriesShow: function (event) {
            var $chevron = $(event.target).parent().find(".chevron");
            $chevron.addClass("icon-chevron-down").removeClass("icon-chevron-right");
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
                this.toggleButtonState($source.parent().parent().parent().find("a.btn"), $source.is(".js-btn-add"));
            } else {
                this.toggleButtonState($source, $source.is(".js-btn-add"));
                if ($source.parent().parent().is(".js-series")) {
                    if ($source.parent().parent().parent().find(".js-btn-add").length <= 0) {
                        this.toggleButtonState($source.parent().parent().parent().parent().find(".js-btn-add.js-btn-module-level"), true);
                    } else {
                        this.toggleButtonState($source.parent().parent().parent().parent().find(".js-btn-remove.js-btn-module-level"), false);
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

        /**
         * Generates a results found string based on what is found in the
         * modules panel list.
         */
        generateResultsText: function () {
            var $things = this.$(".js-modules-list > li:not(.links)"),
                thingsLength = $things.length,
                thingType = "modules",
                resultsText = "Found no results";

            if (thingsLength && !$things.first().hasClass("js-links")) {
                if ($things.first().hasClass("js-series")) {
                    thingType = "series";
                } else if (thingsLength === 1) {
                    thingType = "module";
                }

                resultsText = "Found " + thingsLength + " " + thingType;
            }

            return resultsText;
        },

        updateList: function (fullpath) {
            var self = this;

            $.ajax({
                url: "/" + fullpath + ".children.html?t=" + encodeURIComponent(self.thingPath),
                type: "GET",
                success: function (data) {
                    self.$(".js-modules-list").empty().append(data),
                    self.updateResultsText(self.generateResultsText());
                },
                error: function () {
                    $("#errorModal").modal("show");
                    self.$(".js-modules-list").empty();
                    self.updateResultsText(self.generateResultsText());
                }
            });
        },

        updateResultsText: function (resultsText) {
            this.$(".js-modules-found h3").text(resultsText);
        },

        setHeight: function (height) {
            this.$el.height(height);
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
        ListView: ListView
    };
});
