define(['jquery', 'underscore'], function ($, _) {
	"use strict";

	var Results = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(Results.prototype, {
		initialize: function () {
			_.defaults(this, {
				selector: 'body',
				$el: $(this.selector)
			});
		},

		updateResults: function (thingPath) {
			console.log('selected subject id', thingPath);
			var html = '<li class="clearfix course"><h5 class="pull-left">Language classes</h5><div class="pull-right clearfix"><a class="pull-left more" href="#">more</a><a href="#" class="pull-left btnAddSingleLecture btn">Add</a></div><ul class="courseMoreInfo"><li class="courseSeries clearfix"><div class="pull-left"><h5>An introduction to the language of 16th Century texts.</h5><span class="courseDatePattern">W1</span><span class="courseLocation">Sidgiwck Av.</span><br/><span class="courseLecturer">Dr. W. Bennett, French IA</span></div><a href="#" class="btn pull-right">Add</a></li><li class="courseSeries clearfix"><div class="pull-left"><h5>An introduction to the language of 16th Century texts.</h5><span class="courseDatePattern">W1</span><span class="courseLocation">Sidgiwck Av.</span><br/><span class="courseLecturer">Dr. W. Bennett, French IA</span></div><a href="#" class="btn pull-right">Add</a></li></ul></li>';
        	
        	$.get('/' + thingPath + ".children.html", function (data) {
        		$('ul#resultsList', this.$el).empty().append(data);

        		$('a.more', this.$el).click(function (event) {
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
        	});
		}
	});

	return Results;
});