/*
 * An assert() function. Usage:
 * 
 * assert(1 + 1 == 3, "yay maths"); // raises an AssertionError
 * assert(1 + 1 == 2, "yay maths"); // does nothing
 */
define(["underscore"], function(_) {
    function AssertionError(message, objects) {  
        this.name = "AssertionError";  
        this.message = message || "";
        this.objects = objects;
    }  
    AssertionError.prototype = new Error();  
    AssertionError.prototype.constructor = AssertionError;

    function assert(expression) {
        if (!expression) {
            var objectsStart = 2;
            var message = arguments[1];
            if(!_.isString(message)) {
                objectsStart = 1;
                message = "";
            }
            
            var objects = _.tail(arguments, objectsStart);
            
            if(console && console.error) {
                console.error("assertion failed. expr:",
                        expression, ", message:", message,
                        ", objects:", objects);
            }
            throw new AssertionError(message, objects);
        }
    }
    assert.AssertionError = AssertionError;
    return assert;
});