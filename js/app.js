$(function () {
	"use strict";

	$('a[href="#"]').click(function (event) {
		event.preventDefault();
	});

	//populate results list
	(function populateResults(toAdd) {
		var i,
			$singleResult = $('#search #results ul li');

		for (i = 0; i < toAdd; i += 1) {
			$('#search #results ul').append($singleResult.clone());
		}
	}(12));
});
