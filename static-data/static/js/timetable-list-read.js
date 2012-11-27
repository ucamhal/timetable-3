define(["util/classes", "bootstrap"], function(Classes) {
    "use strict";

    window.Classes = Classes;

    var ctor = function MyClass() {
        MyClass.__super__.constructor.apply(this, arguments);
    }; 
    window.MyClass = Classes.Any.extend({constructor: ctor});

    var Greeter = Classes.Any.extend({
        constructor: function Greeter(name) {
            this.name = name;
        },

        getName: function() {
            return this.name;
        },

        greet: function() {
            return "Hello " + this.getName() + "!";
        }
    });

    var ForgetfullGreeter = Greeter.extend({
        // Provide an explicit constructor function to call up to the
        // superclass's constructor. The benefit of this is that
        // instances of ForgetfullGreeter will have the name of this
        // function visible when inspected in a js debugger, making it
        // easy to see at a glance the type of an object.
        constructor: function ForgetfullGreeter() {
            ForgetfullGreeter.__super__.constructor.apply(this, arguments);
        },

        // Override getName
        getName: function() {
            return "there";
        }
    })

    console.log(new Greeter("Hal").greet());
    console.log(new ForgetfullGreeter("Hal").greet());

    console.log(new ForgetfullGreeter("Hal") instanceof ForgetfullGreeter);
    console.log(new Greeter("Hal") instanceof ForgetfullGreeter);
    console.log(new ForgetfullGreeter("Hal") instanceof Classes.Any);
    console.log(new Greeter("Hal") instanceof Classes.Any);

    return undefined;
});