// ctor, inherits and extend below are originally borrowed from backbone.js.
// (c) 2010-2012 Jeremy Ashkenas, DocumentCloud Inc.
// Backbone may be freely distributed under the MIT license.
// For all details and documentation:
// http://backbonejs.org

/**
 * Helpers for Object Oriented javascript development.
 *
 * Here's an example of using this module to define classes & extend a class
 * to create a subclass:
 *
 *     var Greeter = Classes.Any.extend({
 *         constructor: function Greeter(name) {
 *             this.name = name;
 *         },
 *
 *         getName: function() {
 *             return this.name;
 *         },
 *
 *         greet: function() {
 *             return "Hello " + this.getName() + "!";
 *         }
 *     });
 *
 *     var ForgetfullGreeter = Greeter.extend({
 *         // Provide an explicit constructor function to call up to the
 *         // superclass's constructor. The benefit of this is that
 *         // instances of ForgetfullGreeter will have the name of this
 *         // function visible when inspected in a js debugger, making it
 *         // easy to see at a glance the type of an object.
 *         constructor: function ForgetfullGreeter() {
 *             ForgetfullGreeter.__super__.constructor.apply(this, arguments);
 *         },
 *
 *         // Override getName
 *         getName: function() {
 *             return "there";
 *         }
 *     })
 *
 *     console.log(new Greeter("Hal").greet());           // prints Hello Hal!
 *     console.log(new ForgetfullGreeter("Hal").greet()); // prints Hello there!
 *
 *     console.log(new ForgetfullGreeter("Hal") instanceof ForgetfullGreeter); // prints true
 *     console.log(new Greeter("Hal") instanceof ForgetfullGreeter);           // prints false
 *     console.log(new ForgetfullGreeter("Hal") instanceof Classes.Any);       // prints true
 *     console.log(new Greeter("Hal") instanceof Classes.Any);                 // prints true
 */
define(["underscore"], function(_) {

    var extendRequiresConstructor = true;

    /**
     * Configure this module's extend function to require a constructor property
     * to be included when defining a new class.
     */
    function requireConstructor(yesNo) {
        if(yesNo === undefined) {
            return extendRequiresConstructor;
        }
        extendRequiresConstructor = Boolean(yesNo);
        return extendRequiresConstructor;
    }

    // Shared empty constructor function to aid in prototype-chain creation.
    var ctor = function(){};

    // Helper function to correctly set up the prototype chain, for subclasses.
    // Similar to `goog.inherits`, but uses a hash of prototype properties and
    // class properties to be extended.
    var inherits = function(parent, protoProps, staticProps) {
        var child;

        // The constructor function for the new subclass is either defined by you
        // (the "constructor" property in your `extend` definition), or defaulted
        // by us to simply call the parent's constructor.
        if (protoProps && protoProps.hasOwnProperty('constructor')) {
            child = protoProps.constructor;
        } else {
            // Raise an error if a constructor is required.
            if(extendRequiresConstructor) {
                throw new Error("No 'constructor' function was provided when " +
                    "defining a class. Either call the requireConstructor" +
                    "(false) function of this module, or provide a " +
                    "constructor function. For example: " +
                    "constructor: function MyClass() { MyClass.__super__.constructor.apply(this, arguments); }");
            }
            child = function(){ parent.apply(this, arguments); };
        }

        // Inherit class (static) properties from parent.
        _.extend(child, parent);

        // Set the prototype chain to inherit from `parent`, without calling
        // `parent`'s constructor function.
        ctor.prototype = parent.prototype;
        child.prototype = new ctor();

        // Add prototype properties (instance properties) to the subclass,
        // if supplied.
        if (protoProps) _.extend(child.prototype, protoProps);

        // Add static properties to the constructor function, if supplied.
        if (staticProps) _.extend(child, staticProps);

        // Correctly set child's `prototype.constructor`.
        child.prototype.constructor = child;

        // Set a convenience property in case the parent's prototype is needed later.
        child.__super__ = parent.prototype;

        return child;
    };

    // The self-propagating extend function that Backbone classes use.
    var extend = function (protoProps, classProps) {
        var child = inherits(this, protoProps, classProps);
        child.extend = this.extend;
        return child;
    };

    /**
     * A class which can be used as the root of a class hierachy, much like the
     * Object class in Java.
     */
    function Any() {};
    Any.extend = extend;

    return {
        requireConstructor: requireConstructor,
        Any: Any,
        extend: extend
    }
});