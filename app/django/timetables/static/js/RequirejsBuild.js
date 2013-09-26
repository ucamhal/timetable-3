/**
 * Build profile for django-require.
 *
 * This supports all the normal configuration available to a r.js build profile. The only gotchas are:
 *
 *   - 'baseUrl' will be overidden by django-require during the build process.
 *   - 'appDir' will be overidden by django-require during the build process.
 *   - 'dir' will be overidden by django-require during the build process.
 */
({
    name: "main",

    mainConfigFile: "main.js",

    include: [
        "index-student",
        "index-admin",
        "view/student/student-app",
        "view/admin/page/timetable-calendar",
        "view/admin/page/timetable-list-read",
        "view/admin/page/timetable-list-write",
        "view/admin/page/timetable-overview"
    ],

    // Wrap our code in an anonymous function
    wrap: true,

    // After main.js is renamed to include its hash, the filename no
    // longer matches the module name. To work around this we just
    // hard code the required require() call to main:
    insertRequire: ["main"],

    /*
     * Allow CSS optimizations. Allowed values:
     * - "standard": @import inlining, comment removal and line returns.
     * Removing line returns may have problems in IE, depending on the type
     * of CSS.
     * - "standard.keepLines": Like "standard" but keeps line returns.
     * - "none": Skip CSS optimizations.
     * - "standard.keepComments": Keeps the file comments, but removes line returns.
     * - "standard.keepComments.keepLines": Keeps the file comments and line returns.
     */
    optimizeCss: "standard",

    /*
     * How to optimize all the JS files in the build output directory.
     * Right now only the following values are supported:
     * - "uglify": Uses UglifyJS to minify the code.
     * - "uglify2": Uses UglifyJS2.
     * - "closure": Uses Google's Closure Compiler in simple optimization
     * mode to minify the code. Only available if REQUIRE_ENVIRONMENT is "rhino" (the default).
     * - "none": No minification will be done.
     */
    optimize: "uglify",

    /*
     * By default, comments that have a license in them are preserved in the
     * output. However, for a larger built files there could be a lot of
     * comment files that may be better served by having a smaller comment
     * at the top of the file that points to the list of all the licenses.
     * This option will turn off the auto-preservation, but you will need
     * work out how best to surface the license information.
     */
    preserveLicenseComments: true,

    /*
     * The default behaviour is to optimize the build layers (the "modules"
     * section of the config) and any other JS file in the directory. However, if
     * the non-build layer JS files will not be loaded after a build, you can
     * skip the optimization of those files, to speed up builds. Set this value
     * to true if you want to skip optimizing those other non-build layer JS
     * files.
     */
    skipDirOptimize: false

})