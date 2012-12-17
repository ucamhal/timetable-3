define(["jquery", "underscore"], function ($, _) {
	//Go to the selected timetable when there is a click on the li element
	$("#timetablesOverview ul li:not(.createNewTimetable)").click(function () {
		window.location = $("a", this).attr("href");
	});
	
	var updateTimetablesLockStatus = function updateTimetablesLockStatus () {
		$.ajax({
			url: "",
			success: function (response) {
				console.log("update timetables update lock status success");
				if (response.timetables) {
					for (var timetable in response.timetables) {
						console.log("timetables");
						//$("timetableSelectore").toggleClass("locked", timetables.locked);
					}	
				}
			},
			error: function () {
				console.log("update timetables update lock status failure");
			}
		});
	};
	
	var updateTimetablesLockStatusInterval = setInterval(updateTimetablesLockStatus, 10000);
});