const webpack = require('webpack')
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
    entry: './src/main',
    output: {
        path: path.join(__dirname, 'dist'),
        filename: '[name].js'
    },
    module: {
        loaders: [
            { test: /\.js$/, exclude: /node_modules/, loader: 'babel' },
            { test: /\.vue$/, loader: 'vue' }
        ]
    },
    resolve: {
        extensions: ['', '.js', '.vue', '.json'],
        fallback: [path.join(__dirname, 'node_modules')],
        alias: {
          'src': path.resolve(__dirname, 'src'),
          'assets': path.resolve(__dirname, 'src', 'assets'),
          'components': path.resolve(__dirname, 'src', 'components')
        }
    },
    resolveLoader: {
        fallback: [path.join(__dirname, 'node_modules')]
    },
    devServer: {
        historyApiFallback: true,
        hot: true,
        inline: true,
        progress: true,
    },
    externals: {
        'jquery': 'jQuery',
        'vue': 'Vue',
        'vue-router': 'VueRouter',
        'vue-resource': 'VueResource',
        'moment': 'moment'
    },
    plugins: [
        new webpack.optimize.OccurrenceOrderPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoErrorsPlugin(),
        new HtmlWebpackPlugin({
          filename: 'index.html',
          template: 'index.html',
          inject: true
        })
    ]
}