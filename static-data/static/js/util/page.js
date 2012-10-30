define(['jquery'], function ($) {
	"use strict";
	
	/**
	 * On the page data is loaded to idenfiy the page. This module extracts that information and 
	 * makes it available to to other modules.
	 */
	var _crsfToken, _pageThingPath, _isstaff;
	var _check_is_staff = function() {
		if ( _isstaff === undefined ) {
			if ( $("#userinfo").length == 1 ) {
				_isstaff = ($("#userinfo").attr("userrole") === "staff")
			} else if (  $("#thinginfo").length == 1 ) {
				_isstaff = ($("#thinginfo").attr("userrole") === "staff" )
			}
		}
		return _isstaff;
	};
	var _adminEnabled = _check_is_staff();

	return {
		getThingPath : function() {
			if ( _pageThingPath === undefined ) {
				if ( $("#userinfo").length == 1 ) {
					_pageThingPath = 'user/' + $("#userinfo").attr("userid");
				} else if (  $("#thinginfo").length == 1 ) {
					_pageThingPath = $("#thinginfo").attr("fullpath");
				}
			}
			return _pageThingPath;
		},
		getCrsf : function() {
			if ( _crsfToken === undefined ) {
				if ( $("#userinfo").length == 1 ) {
					_crsfToken = $("#userinfo").find("[name=csrfmiddlewaretoken]").val()
				} else if (  $("#thinginfo").length == 1 ) {
					_crsfToken = $("#thinginfo").find("[name=csrfmiddlewaretoken").val()
				}
			}
			return _crsfToken;
		},
		adminEnabled : function() {
			return _adminEnabled;
		},
		isStaff : _check_is_staff,
		enableAdmin : function() {
			if ( _check_is_staff() ) {
				_adminEnabled = true;
			}
		},
		disableAdmin : function() {
			if ( _check_is_staff() ) {
				_adminEnabled = false;
			}
		}
	}
});