define(["jquery"], function ($) {
    "use strict";

    /**
     * On the page data is loaded to idenfiy the page. This module extracts that information and 
     * makes it available to to other modules.
     */
    var _crsfToken,
        _pageThingPath,
        _isstaff,
        _check_is_staff = function () {
            if (_isstaff === undefined) {
                if ($("#userinfo").length === 1) {
                    _isstaff = ($("#userinfo").data("userrole") === "staff");
                } else if ($("#thinginfo").length === 1) {
                    _isstaff = ($("#thinginfo").data("userrole") === "staff");
                }
            }
            return _isstaff;
        },
        _adminEnabled = _check_is_staff(),
        _googleAnalyticsID,
        _userRole,
        _userTripos;

    return {
        getUserTripos: function () {
            return _userTripos = _userTripos || $("#userinfo").data("tripos");
        },
        isUserLoggedIn: function () {
            return Boolean($("#userinfo").data("logged-in"));
        },
        getGoogleAnalyticsID: function () {
            _googleAnalyticsID = _googleAnalyticsID || $(".js-ga-info").data("id");
            return _googleAnalyticsID;
        },
        getUserRole: function () {
            _userRole = _userRole || $("#userinfo").data("userrole");
            return _userRole;
        },
        getThingPath : function () {
            if (_pageThingPath === undefined) {
                if ($("#userinfo").length === 1) {
                    _pageThingPath = "user/" + $("#userinfo").data("userid");
                } else if ($("#thinginfo").length === 1) {
                    _pageThingPath = $("#thinginfo").data("fullpath");
                }
            }
            return _pageThingPath;
        },
        getCrsf : function () {
            if (_crsfToken === undefined) {
                if ($("#userinfo").length === 1) {
                    _crsfToken = $("#userinfo").find("[name=csrfmiddlewaretoken]").val();
                } else if ($("#thinginfo").length === 1) {
                    _crsfToken = $("#thinginfo").find("[name=csrfmiddlewaretoken").val();
                }
            }
            return _crsfToken;
        },
        adminEnabled : function () {
            return _adminEnabled;
        },
        isStaff : _check_is_staff,
        enableAdmin : function () {
            if (_check_is_staff()) {
                _adminEnabled = true;
            }
        },
        disableAdmin : function () {
            if (_check_is_staff()) {
                _adminEnabled = false;
            }
        }
    };
});
