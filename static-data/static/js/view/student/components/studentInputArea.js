define(["jquery", "underscore", "view/base/components/baseInputArea"], function ($, _, BaseInputArea) {
	"use strict";

	var StudentInputArea = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(StudentInputArea.prototype, BaseInputArea.prototype);
	_.extend(StudentInputArea.prototype, {
		initialize: function () {

			/*
			$("#iAmInputText").typeahead({
				source: (function () {
					var results = [];
					$("#iAmInput option").each(function () {
						results.push($.trim($(this).text()));
					});
					console.log(results);
					return results;
				}())
			});
			*/
		}
	});

	return StudentInputArea;
});