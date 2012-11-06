define([
	"jquery",
	"underscore",
	"view/base/components/baseResults"
], function ($, _, BaseResults, page) {
	"use strict";

	var StudentResults = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(StudentResults.prototype, BaseResults.prototype);
	_.extend(StudentResults.prototype, {
		initialize: function () {
			

		}
	});

	return StudentResults;
});