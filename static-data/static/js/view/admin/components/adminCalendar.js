define([
	"jquery",
	"underscore",
	"view/admin/components/calendarComponents/listView"
], function ($, _, ListView) {

	var AdminCalendar = function (opt) {
		_.extend(this, opt);
		this.initialize();
	};

	_.extend(AdminCalendar.prototype, {
		initialize: function () {
			_.defaults(this, {
				listView: new ListView({
					selector: "#adminListView"
				}),
				selector: "body",
				$el: $(this.selector)
			});
		}
	});

	return AdminCalendar;
});