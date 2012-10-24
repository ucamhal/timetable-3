define(['jquery', 'underscore', 'util/page'], function ($, _, page) {
	"use strict";

	var Results = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Results.prototype, {
		initialize: function () {
			var self = this;

			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector)
			});

			$("a.more", this.$el).live('click', function () {
				switch ($(this).text()) {
				case 'more':
					$(this).text('show less');
					$('.courseMoreInfo', $(this).parent().parent()).slideDown('fast');
					break;
				case 'show less':
					$(this).text('more');
					$('.courseMoreInfo', $(this).parent().parent()).slideUp('fast');
					break;
				}

				event.preventDefault();
			});

			$("a.btn-add, a.btn-remove", this.$el).live("click", function (event) {
				if ($(this).is('.btnAddSingleLecture')) {
					self.associate($(this).parent().parent().find("a.btn"), $(this).is(".btn-add"));
				} else {
					self.associate($(this), $(this).is(".btn-add"));
					if ($(this).parent().parent().is(".courseMoreInfo")) {
						if ($(this).parent().parent().find(".btn-add").length <= 0) {
							self.toggleButtonState($(this).parent().parent().parent().find(".btn-add.btnAddSingleLecture"), true);
						} else {
							self.toggleButtonState($(this).parent().parent().parent().find(".btn-remove.btnAddSingleLecture"), false);
						}
					}
				}

				event.preventDefault();
			});

		},

		toggleButtonState: function ($btn, fromAdd) {
			if (fromAdd === true) {
				$btn.removeClass("btn-add btn-success").addClass("btn-remove btn-danger").text("Remove");
			} else {
				$btn.removeClass("btn-remove btn-danger").addClass("btn-add btn-success").text("Add");
			}
		},

		updateResults: function (thingPath) {
			var self = this,
				resultsLength,
				textToChange;
			console.log('selected subject id', thingPath);
        	
        	$.get('/' + thingPath + ".children.html?t="+encodeURIComponent(page.getThingPath()), function (data) {
        		resultsLength = $('ul#resultsList', self.$el).empty().append(data).find("> li").length;

        		if (resultsLength === 1) {
        			textToChange = "Found 1 module";
        		} else {
    				textToChange = "Found " + resultsLength + " modules";
        		}

        		$("> h3", self.$el).text(textToChange);
        	});
		},
		associate: function (source, add) {
			var self = this;
			var sourcepath = page.getThingPath();
			var crsf = page.getCrsf();
			var postdata  = {}
			if ( add ) {
				postdata['t'] = $(source).attr("data-fullpath");
				postdata['es'] = $(source).attr("data-eventsourceid");
				postdata['e'] = $(source).attr("data-eventid");
			} else {
				postdata['td'] = $(source).attr("data-fullpath");
				postdata['esd'] = $(source).attr("data-eventsourceid");
				postdata['ed'] = $(source).attr("data-eventid");
			}
			postdata['csrfmiddlewaretoken'] = crsf;
			$.post(sourcepath+".link", postdata, function() {
				self.toggleButtonState($(source), add);
				self.dispatchEvent("timetableChanged");
			}).error(function() {
				alert("Failed to "+(add?"add":"remove")+" items");
			});
		},

		addEventListener: function (eventName, callback) {
			this.$el.bind(eventName, callback);
		},

		dispatchEvent: function (eventName) {
			this.$el.trigger(eventName);
		},

		resize: function () {
			var topOffset = this.$el.offset().top;
			var heightToSet = $(window).height() - 30 - topOffset;
			this.$el.height(heightToSet);
		}
	});

	return Results;
});