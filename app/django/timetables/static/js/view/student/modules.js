define([
    "jquery",
    "underscore",
    "backbone",
    "util/api-student",
    "util/dialog-factory-student",
    "util/page",
    "util/focus-helper",
    "util/underscore-mixins"
], function ($, _, Backbone, api, dialogFactory, page, focusHelper) {
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

        events: function () {
            return {
                "hidden": this.onSeriesHidden,
                "hide" : this.onSeriesHide,
                "show" : this.onSeriesShow,
                // The module click callback shouldn't be executed more than
                // once every 200ms.
                "click a.js-btn-add, a.js-btn-remove" : _.throttle(this.moduleButtonClickHandler, 200, {
                    trailing: false
                })
            };
        },

        onSeriesHidden: function (event) {
            var $hiddenContent = $(event.target);
            $hiddenContent.addClass("collapsed");
        },

        onSeriesHide: function (event) {
            var $chevron = $(event.target).parent().find(".chevron"),
                $button = $chevron.parent();
            $chevron.removeClass("icon-chevron-down").addClass("icon-chevron-right");
            $button.attr("aria-pressed", "false");
        },

        onSeriesShow: function (event) {
            var $target = $(event.target),
                $chevron = $target.parent().find(".chevron"),
                $button = $chevron.parent();
            $target.removeClass("collapsed");
            $chevron.addClass("icon-chevron-down").removeClass("icon-chevron-right");
            $button.attr("aria-pressed", "true");
        },

        associate: function ($source, add) {
            var self = this,
                userPath = this.thingPath,
                fullpath = $source.attr("data-fullpath"),
                crsf = this.crsfToken,
                eventsourceId = $source.attr("data-eventsourceid"),
                eventId = $source.attr("data-eventid"),
                apiRequest = add === true ? api.addToTimetable : api.removeFromTimetable;

            // Set the saving state to true. This prevents more add/remove
            // request from happening until this request has finished.
            this.isSaving(true);

            apiRequest(userPath, fullpath, eventsourceId, eventId, crsf, function (error) {
                if (error) {
                    // If the error has no code (logged out of raven/shib or
                    // network error) we shouldn't show them the login error.
                    // The canary watcher will take care of showing the
                    // appropriate message.
                    if (error.code) {
                        if (error.code !== 403) {
                            // An unknown error has occured
                            $("#errorModal").modal("show");
                            return;
                        } else if (!page.isUserLoggedIn()) {
                            // If the error is a 403 and the page thinks the
                            // user is logged in it means the session has
                            // expired (if the user isn't doing something he 
                            // isn't supposed to be doing). Canary will jump in
                            // and show the appropriate error.
                            // Otherwise we can just show the log in modal:
                            this.showNotSignedInError($source);
                        }
                        // An unknown error has occured
                        var errorDialog = dialogFactory.unknownError();
                        // Refocus the clicked add button when the error dialog
                        // closes.
                        self.listenTo(errorDialog, "close", function () {
                            focusHelper.focusTo($source);
                        });

                    }
                    // Stop executing the code
                    return;
                }

                self.updateButtonStates($source);
                _.dispatchEvent(self, "timetableUpdated");
                // Remove the saving state so modules can be removed/added again
                self.isSaving(false);
            });
        },

        updateButtonStates: function ($source) {
            if ($source.is(".js-btn-module-level")) {
                this.toggleButtonState($source.parent().parent().parent().find("a.btn"), $source.is(".js-btn-add"));
            } else {
                this.toggleButtonState($source, $source.is(".js-btn-add"));
                if ($source.parent().parent().is(".js-series")) {
                    var $module = $source.parent().parent().parent();
                    if ($module.find(".js-btn-remove").length) {
                        // If any of the series have been added, the module
                        // button should become a remove button.
                        this.toggleButtonState($module.parent().find(".js-btn-add.js-btn-module-level"), true);
                    } else {
                        // Module button should show "Add"
                        this.toggleButtonState($module.parent().find(".js-btn-remove.js-btn-module-level"), false);
                    }
                }
            }
        },

        toggleButtonState: function ($btn, fromAdd) {
            $btn.each(function () {
                var buttonType = "series",
                    $target = $(this);
                if ($(this).hasClass("js-btn-module-level")) {
                    buttonType = "module";
                }

                if (fromAdd === true) {
                    // Change the button to a remove button
                    $target.removeClass("js-btn-add btn-success").addClass("js-btn-remove btn-danger");
                    $target.text("Remove").attr("aria-label", "Remove " + buttonType + " from timetable");
                    return;
                }

                // Change the button to an add button
                $target.removeClass("js-btn-remove btn-danger").addClass("js-btn-add btn-success");
                $target.text("Add").attr("aria-label", "Add " + buttonType + " to timetable");
            });
        },

        isSaving: function (saving) {
            if (saving === undefined) {
                return this.saving;
            }
            this.saving = saving;
        },

        showNotSignedInError: function ($refocusTarget) {
            var selection = "";

            if (Backbone.history.fragment) {
                selection = "#" + Backbone.history.fragment;
            }

            var notSignedInError = dialogFactory.notSignedInError({
                selection: encodeURIComponent(selection)
            });

            if ($refocusTarget.length) {
                this.listenTo(notSignedInError, "close", function () {
                    focusHelper.focusTo($refocusTarget);
                });
            }
        },

        moduleButtonClickHandler: function (event) {
            // If the user isn't logged in prompt to login
            if (!page.isUserLoggedIn()) {
                this.showNotSignedInError($(event.currentTarget));
                return;
            }

            // If one of the modules is still in the process of saving, prevent
            // the button from being clicked.
            if (this.isSaving()) {
                return;
            }

            var $target = $(event.currentTarget);
            if ($target.is(".js-btn-module-level")) {
                this.associate($target.parent().parent().find("a.btn"), $target.is(".js-btn-add"));
            } else {
                this.associate($target, $target.is(".js-btn-add"));
            }

            return false;
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
            var self = this,
                userPath = this.thingPath;

            api.getModulesList(fullpath, userPath, function (error, response) {
                self.$(".js-modules-list").empty();

                if (error && error.code) {
                    var $focussedEl = $(document.activeElement),
                        errorDialog = dialogFactory.unknownError();
                    self.listenTo(errorDialog, "close", function () {
                        focusHelper.focusTo($focussedEl);
                    });
                    self.updateResultsText(self.generateResultsText());
                    return;
                }

                self.$(".js-modules-list").append(response),
                self.updateResultsText(self.generateResultsText());
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
            var self = this,
                userPath = self.thingPath,
                year = self.activeDate.getFullYear(),
                month = self.activeDate.getMonth() + 1;

            api.getUserEventsList(userPath, year, month, function (error, response) {
                if (error && error.code) {
                    var $focussedEl = $(document.activeElement),
                        errorDialog = dialogFactory.unknownError();
                    self.listenTo(errorDialog, "close", function () {
                        focusHelper.focusTo($focussedEl);
                    });

                    return;
                }

                self.$el.empty().append(response);
            });
        }
    });

    return {
        ModulesList: ModulesList,
        ListView: ListView
    };
});
