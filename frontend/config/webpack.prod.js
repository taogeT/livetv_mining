const path = require('path')
const dirname = path.join(__dirname, '..')
const webpack = require('webpack')
const merge = require('webpack-merge')
const baseWebpackConfig = require('./webpack.base')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const CleanWebpackPlugin = require('clean-webpack-plugin')

module.exports = merge(baseWebpackConfig, {
    devtool: '#source-map',
    plugins: [
        new CleanWebpackPlugin(['dist'], { root: dirname }),
        new webpack.optimize.UglifyJsPlugin({
            sourceMap: true,
            compress: {
                warnings: false
            }
        }),
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index.html',
            minify: {
                removeComments: true,
                collapseWhitespace: true,
                removeAttributeQuotes: true
            },
            chunksSortMode: (a, b) => {
                const orders = ['manifest', 'vendor', 'components', 'app']
                return orders.indexOf(a.names[0]) - orders.indexOf(b.names[0])
            }
        })
    ]
})