var webpack = require('webpack');
var path = require('path');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  devServer: {
    host: process.env.DEVSERVER_HOST || "0.0.0.0",
    port: process.env.DEVSERVER_PORT || "8080",
    config: "webpack.dev.config.js",
    https: process.env.DEVSERVER_HTTPS ? true : false,
    stats: 'minimal',
  },
  entry: {
    reporting: './src/reporting/main',
    manageusers: './src/manageusers/main',
    nonuseroutreach: './src/nonuseroutreach/main',
    myprofile: './src/myprofile/main',
    analytics: './src/analytics/main',
    custom: './src/sass/custom.scss',
    customanalytics: './src/sass/analytics.scss',
    bootstrapdaterange: './src/sass/vendor/bootstrap-daterange.scss',
    seo_base_styles: './src/sass/seo_base_styles.scss',
    seo_base_scripts: './src/v2/seo-base-scripts',
  },
  resolve: {
    root: path.resolve('src'),
    extensions: ['', '.js', '.jsx'],
  },
  output: {
    path: '../static/bundle',
    filename: '[name].js',
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          cacheDirectory: true,
        },
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'eslint-loader',
      },
      {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract('css!sass')
      }
    ],
    sassLoader: {
      includePaths: [path.resolve(__dirname, "../static")]
    },
  },
  eslint: {
    failOnWarning: true,
    failOnError: true,
  },
  plugins: [
    // React is smaller, faster, and silent in this mode.
    // The warning module is also silent in this mode.
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': '"production"',
    }),
    // Dedupe slightly decreases output size.
    new webpack.optimize.DedupePlugin(),
    // Webpack docs recommend using this plugin.
    // It slightly decreasese output size.
    new webpack.optimize.OccurenceOrderPlugin(),
    // Minify.
    // Warnings are off as the output isn't useful in a log.
    // In development it can be useful to see this output to verify that
    // dead code removal is doing something sane.
    new webpack.optimize.UglifyJsPlugin({compress: {warnings: false}}),
    new ExtractTextPlugin('[name].css'),
  ],
};
