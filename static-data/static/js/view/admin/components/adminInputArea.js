define([
	"jquery",
	"underscore",
	"view/base/components/baseInputArea"
], function ($, _, BaseInputArea) {

	var AdminInputArea = function (opt) {
		_.extend(this, opt);
		this.initialize();
		this.baseInitialize();
	};

	_.extend(AdminInputArea.prototype, BaseInputArea.prototype);
	_.extend(AdminInputArea.prototype, {
		initialize: function () {
		}
	});

	return AdminInputArea;
});