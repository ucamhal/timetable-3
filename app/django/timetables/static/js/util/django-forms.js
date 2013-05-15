/**
 * This module provides support for building Django forms compatible
 * POST bodies from a JSON representation of a form. This can be used to
 * assemble form data without actually using an HTML form.
 */
define(["underscore", "jquery", "util/assert"], function(_, $, assert) {
    "use strict";

    /**
     * Encodes a JSON representation of a Django form into a
     * representation sutable for POSTing to a Django form accepting
     * endpoint.
     *
     * The following is an example form with a nested formset named
     * "events" containing a single form (with 2 initially).
     *
     * {
     *     "title": "The Brittonic-speaking peoples (Paper 3)",
     *     "events": {
     *         "initial": 2,
     *         "max": 10,
     *         "forms": [
     *             {
     *                 "title": "Pictish Kingdoms aa",
     *                 "event_type": "Lecture"
     *             }
     *         ]
     *     }
     * }
     */
    function encodeJSONForm(jsonForm) {
        return $.param(compressJSONForm(jsonForm));
    }

    /**
     * Recursively flatten the structure of a JSON form into dest.
     *
     * The form is flattened by joining the keys at any given level with
     * the joined key of the preceding level.
     *
     * @param jsonForm A JSON object such as the one in the above
     *        example.
     * @param prefix (optional) The string prefix to use when flattening
     *        this form. Default is the empty string.
     * @param dest (optional) A JS object to place the flattened
     *        key/values into. Default: an empty object.
     * @return The dest param object containing the flattened form.
     */
    function compressJSONForm(jsonForm, prefix, dest) {
        dest = dest || {};
        prefix = prefix || "";

        assert(_.isObject(dest), dest);
        assert(_.isString(prefix), prefix);

        _.each(jsonForm, function(value,  key) {
            if (_.isObject(value)) {
                compressJSONFormset(value, join(prefix, key), dest);
            } else {
                merge(dest, join(prefix, key), value);
            }
        });

        return dest;
    }

    /**
     * As compressJSONForm, except the first param is a JSON formset
     * containing "initial", "max" and "forms" keys. See the example
     * at the top.
     */
    function compressJSONFormset(jsonFormset, prefix, dest) {
        dest = dest || {};
        prefix = prefix || "";

        assert(_.isObject(dest), dest);
        assert(_.isString(prefix), prefix);

        compressManagementFormset(jsonFormset, prefix, dest);

        _.each(jsonFormset.forms, function(form, index) {
            var formPrefix = join(prefix, String(index));
            compressJSONForm(form, formPrefix, dest);
        });
    }

    /** 
     * Builds, flattens and inserts a management form for the provided
     * formset into dest.
     */
    function compressManagementFormset(jsonFormset, prefix, dest) {
        dest = dest || {};
        prefix = prefix || "";

        assert(_.isObject(dest), dest);
        assert(_.isString(prefix), prefix);

        var initial = jsonFormset.initial;
        var max = jsonFormset.max || "";
        var forms = jsonFormset.forms;

        assert(_.isNumber(initial), initial);
        assert(max === "" || _.isNumber(max), max);
        assert(_.isArray(forms), forms);

        merge(dest, join(prefix, "TOTAL_FORMS"), forms.length);
        merge(dest, join(prefix, "INITIAL_FORMS"), initial);
        merge(dest, join(prefix, "MAX_NUM_FORMS"), max);
    }

    /**
     * Add a form key and value to a compressed form, raising an error
     * if the key already exists (it shouldn't).
     */
    function merge(compressedForm, key, value) {
        if(_.has(compressedForm, key)) {
            assert(false, "Duplicate form key", {
                compressedForm: compressedForm,
                key: key,
                value: value
            });
        }
        compressedForm[key] = value;
    }

    /** Join a form key with a prefix. */
    function join(prefix, suffix) {
        if (!prefix) {
            return suffix;
        }
        return [prefix, suffix].join("-");
    }

    return {
        encodeJSONForm: encodeJSONForm
    };
});
