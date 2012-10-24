define([
	"jquery",
	"underscore"
], function ($, _) {
	"use strict";

	var Application = function () {
		this.initialize();
	}

	_.extend(Application.prototype, {

		initialize: function () {
			
			$("#resultsList li a").click(function (event) {
				switch ($(this).text()) {
				case "view":
					$(".courseMoreInfo", $(this).parent().parent().parent()).slideDown();
					break;
				}
				event.preventDefault();
			});

		}

	});

	return Application;
});
