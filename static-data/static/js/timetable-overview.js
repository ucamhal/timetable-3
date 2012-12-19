define(["jquery", "underscore", "backbone"], function ($, _, Backbone) {
	//Go to the selected timetable when there is a click on the li element
	$("#timetablesOverview ul li:not(.createNewTimetable)").click(function () {
		window.location = $("a", this).attr("href");
	});
	
	$( "select.js-select-faculty" ).change( function(){
		var target = $(this).val();
		$(window.location).attr('href', '/' + target + '.home.admin.html');
	});
	
	var timetables = [];
	
	
	var EditableTimetable = Backbone.View.extend({
		initialize: function (opts) {
			console.log("timetable initialization");
		},
		
		setBeingEdited: function (isBeingEdited, by) {
			if (isBeingEdited === true) {
				this.$(".timetableTop").html("Begin edited by <strong>" + by + "</strong>");	
			} else {
				this.$(".timetableTop").html("");
			}
		}
	});
	
	$("#timetablesOverview li.editable").each(function (index, item) {
		timetables.push(new EditableTimetable({
			el: this
		}));
	});
	
	var updateTimetablesLockStatus = function updateTimetablesLockStatus () {
		$.ajax({
			url: "",
			success: function (response) {
				console.log("timetables update lock status success");
				if (response.timetables) {
					for (var i = 0; i < timetables.length; i += 1) {
						var target = timetables[i];
						//do something with response
					}
				}
			},
			error: function () {
				console.log("timetables update lock status failure");
			}
		});
	};
	
	var updateTimetablesLockStatusInterval = setInterval(updateTimetablesLockStatus, 10000);
});