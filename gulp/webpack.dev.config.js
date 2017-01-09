var prodConfig = require('./webpack.config.js');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

// In development we want css extracted but no other plugins to run.
// Keep the production plugin so these two files don't get out of sync.
prodConfig.plugins = prodConfig.plugins.filter(
  p => p instanceof ExtractTextPlugin);

// In development we still want our modules built even when eslint is
// complaining.
prodConfig.eslint = {};

prodConfig.watchOptions = {poll: 1000};

module.exports = prodConfig;
