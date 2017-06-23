const webpack = require('webpack')
const merge = require('webpack-merge')
const baseWebpackConfig = require('./webpack.base')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = merge(baseWebpackConfig, {
    output: {
        filename: 'js/[name].[hash:7].js'
    },
    devtool: '#eval-source-map',
    devServer: {
        overlay: {
          warnings: true,
          errors: true
        },
        hot: true
    },
    plugins: [
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoEmitOnErrorsPlugin(),
        new webpack.SourceMapDevToolPlugin({
            filename: '[file].map',
        }),
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index.html',
            chunksSortMode: (a, b) => {
                const orders = ['manifest', 'vendor', 'components', 'app']
                return orders.indexOf(a.names[0]) - orders.indexOf(b.names[0])
            }
        })
    ]
})