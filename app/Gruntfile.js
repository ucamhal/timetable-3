/* global module */
module.exports = function (grunt) {
    "use strict";

    /**
     * 'grunt jshint' validates all javascript we've written ourselves
     * 
     * 'grunt watch:js' runs grunt jshint whenever a javascript file is saved
     * 
     * 'grunt build' optimizes and minifies all js/css/img into the
     * static-data/build folder
     *
     * 'grunt requirejs' only optimize/minify the js files
     *
     * 'grunt cssmin' only optimize/minify the css files
     *
     * 'grunt imagemin' only optimize the images
     */


    grunt.loadNpmTasks("grunt-contrib-watch");
    grunt.loadNpmTasks("grunt-contrib-jshint");
    grunt.loadNpmTasks("grunt-contrib-requirejs");
    grunt.loadNpmTasks("grunt-contrib-cssmin");
    grunt.loadNpmTasks("grunt-contrib-imagemin");

    var jsBasePath = "django/timetables/static/js/",
        jsFiles = [
            jsBasePath + "*.js",
            jsBasePath + "view/**/*.js",
            jsBasePath + "util/**/*.js",
            "Gruntfile.js"
        ];

    grunt.initConfig({
        pkg: grunt.file.readJSON("package.json"),
        jshint: {
            all: jsFiles,
            options: {
                jshintrc: ".jshintrc"
            }
        },
        requirejs: {
            compile: {
                options: {
                    baseUrl: jsBasePath,
                    mainConfigFile: jsBasePath + "main.js",
                    dir: "static-build/js",
                    name: "libs/require"
                }
            }
        },
        cssmin: {
            minify: {
                cwd: "django/timetables/static/css",
                expand: true,
                src: [
                    "**/*.css"
                ],
                dest: "static-build/css/"
            }
        },
        imagemin: {
            minify: {
                files: [{
                    expand: true,
                    cwd: "django/timetables/static/img",
                    src: "{,*/}*.{png,jpg,jpeg}",
                    dest: "static-build/img"
                }]
            }
        },
        watch: {
            js: {
                files: jsFiles,
                tasks: [
                    "jshint"
                ]
            }
        }
    });

    // Task that builds optimized versions of all static files and moves them
    // into the static-data/build directory
    grunt.registerTask("build", [
        "requirejs",
        "cssmin",
        "imagemin"
    ]);
};
