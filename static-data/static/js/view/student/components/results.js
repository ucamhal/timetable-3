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
			console.log('selected subject id', thingPath);
			var html = '<li class="clearfix course"><h5 class="pull-left">Language classes</h5><div class="pull-right clearfix"><a class="pull-left more" href="#">more</a><a href="#" class="pull-left btnAddSingleLecture btn">Add</a></div><ul class="courseMoreInfo"><li class="courseSeries clearfix"><div class="pull-left"><h5>An introduction to the language of 16th Century texts.</h5><span class="courseDatePattern">W1</span><span class="courseLocation">Sidgiwck Av.</span><br/><span class="courseLecturer">Dr. W. Bennett, French IA</span></div><a href="#" class="btn pull-right">Add</a></li><li class="courseSeries clearfix"><div class="pull-left"><h5>An introduction to the language of 16th Century texts.</h5><span class="courseDatePattern">W1</span><span class="courseLocation">Sidgiwck Av.</span><br/><span class="courseLecturer">Dr. W. Bennett, French IA</span></div><a href="#" class="btn pull-right">Add</a></li></ul></li>';
        	
        	$.get('/' + thingPath + ".children.html?t="+encodeURIComponent(page.getThingPath()), function (data) {
        		$('ul#resultsList', this.$el).empty().append(data);
        	});
		},
		associate : function (source, add) {
			var self = this;
			var sourcepath = page.getThingPath();
			var crsf = page.getCrsf();
			var postdata  = {}
			if ( add ) {
				postdata['t'] = $(source).attr("data-fullpath");
			} else {
				postdata['td'] = $(source).attr("data-fullpath");
			}
			postdata['csrfmiddlewaretoken'] = crsf;
			$.post(sourcepath+".link", postdata, function() {
				self.toggleButtonState($(source), add);
			}).error(function() {
				alert("Failed to "+(add?"add":"remove")+" items");
			});
		},
	});

	return Results;
});