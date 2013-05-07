module.exports = function (grunt) {

    var jsBasePath = 'static-data/static/js/',
        jsFiles = [
            jsBasePath + '*.js',
            jsBasePath + 'view/**/*.js',
            jsBasePath + 'util/**/*.js'
        ];

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jshint: {
            all: jsFiles,
            options: {
                quotmark: "double",
                curly: true,
                browser: true,
                laxbreak : true,
                eqeqeq : true,
                forin: true,
                indent: 4,
                newcap: true,
                plusplus: true,
                undef: true,
                strict: true,
                trailing: true,
                devel: true,
                globals: {
                    require: false,
                    define: false
                }
            }
        },
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
};
