var gulp = require('gulp');
var browserify = require('browserify');
var babelify= require('babelify');
var util = require('gulp-util');
var buffer = require('vinyl-buffer');
var source = require('vinyl-source-stream');
var uglify = require('gulp-uglify');
var sourcemaps = require('gulp-sourcemaps');
var stripDebug = require('gulp-strip-debug');
var gulpif = require('gulp-if');
// var es5shim = require('es5-shim');

var vendor_libs = [
    'react',
    'react-dom',
    'redux',
    'react-redux',
    'babel/polyfill',
    'es6-promise',
    // 'es5-shim'
];

var dest = '../static/bundle';

var strip_debug = true;

// Splitting vendor libs into a separate bundle improves rebuild time from 8
// seconds to <500ms.
gulp.task('vendor', function() {
    return browserify([], { debug: true, list: true, })
    .require(vendor_libs)
    .bundle()
    .on('error', function(error, meta) {
        util.log("Browserify error:", error.toString());
    })
    .pipe(source('vendor.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({loadMaps: true}))
    .pipe(uglify({ mangle: false }))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
});

// If an app task starts logging that it is including packages, add those
// packages to vendor_libs.
gulp.task('reporting', function() {
    return browserify([], {
        debug: true,
        paths: ['./src'],
    })
    .external(vendor_libs)
    .add('src/reporting/main.js')
    .transform(babelify)
    .bundle()
    .on('error', function(error, meta) {
        util.log("Browserify error:", error.toString());
        // Unstick browserify on some errors. Keeps watch alive.
        this.emit('end');
    })
    .on('package', function(pkg) {
        util.log("Including package:", pkg.name)
    })
    .pipe(source('reporting.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({loadMaps: true}))
    // Do we want this in production builds?
    //.pipe(uglify({ mangle: false }))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
});

// If an app task starts logging that it is including packages, add those
// packages to vendor_libs.
gulp.task('manageusers', function() {
    return browserify([], {
        debug: true,
        paths: ['./src'],
    })
    .external(vendor_libs)
    .add('src/manageusers/manageusers.js')
    .transform(babelify)
    .bundle()
    .on('error', function(error, meta) {
        util.log("Browserify error:", error.toString());
        // Unstick browserify on some errors. Keeps watch alive.
        this.emit('end');
    })
    .on('package', function(pkg) {
        util.log("Including package:", pkg.name)
    })
    .pipe(source('manageusers.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({loadMaps: true}))
    // Do we want this in production builds?
    .pipe(uglify({ mangle: false }))
    // stripDebug() must come before sourcemaps.write()
    // .pipe(stripDebug())
    .pipe(gulpif(strip_debug, stripDebug()))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest))
});

gulp.task('build', ['vendor', 'manageusers']);

// Leave this running in development for a pleasant experience.
gulp.task('watch', function() {
    console.log("By default, gulp watch strips console and debugger statements.");
    console.log("To keep them, run: gulp watch-no-strip");
    gulp.watch('src/**/*', ['manageusers']);
});


gulp.task('watch-no-strip', function() {
    console.log("Keeping console and debugger statements.");
    strip_debug = false;
    gulp.watch('src/**/*', ['manageusers']);
});


strip_debug




gulp.task('default', ['build']);
