const path = require('path')
const dirname = path.join(__dirname, '..')
const webpack = require('webpack')
const ExtractTextPlugin = require("extract-text-webpack-plugin")
const CleanWebpackPlugin = require('clean-webpack-plugin')

module.exports = {
    entry: {
        app: path.join(dirname, 'src', 'main.js')
    },
    output: {
        path: path.join(dirname, 'dist'),
        filename: 'js/[name].[chunkhash:7].js',
        chunkFilename: 'js/[name].[chunkhash:7].js'
    },
    module: {
        rules: [
            { test: /\.js$/, exclude: /node_modules/, use: [{ loader: 'babel-loader' }] },
            { test: /\.vue$/, use: [{ loader: 'vue-loader' }] },
            { test: /\.md$/, use: [{ loader: 'vue-markdown-loader' }] },
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: "css-loader"
                })
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.vue', '.json'],
        modules: [path.join(dirname, 'node_modules')],
        alias: {
            components: path.resolve(dirname, 'src', 'components'),
            filters: path.resolve(dirname, 'src', 'filters'),
            resource: path.resolve(dirname, 'src', 'resource'),
            router: path.resolve(dirname, 'src', 'router'),
            store: path.resolve(dirname, 'src', 'store'),
            views: path.resolve(dirname, 'src', 'views'),
            src: path.resolve(dirname, 'src')
        }
    },
    resolveLoader: {
        modules: [path.join(dirname, 'node_modules')]
    },
    externals: {
        'jquery': 'jQuery',
        'vue': 'Vue',
        'vue-router': 'VueRouter',
        'vuex': 'Vuex',
        'vue-resource': 'VueResource',
        'moment': 'moment'
    },
    plugins: [
        new CleanWebpackPlugin(['dist'], { root: dirname }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            minChunks: function(module){
                return module.context && module.context.indexOf("node_modules") != -1;
            }
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'components',
            minChunks: function(module){
                return module.context && module.context.indexOf("src/components") != -1;
            },
            chunks: ['app']
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: "manifest",
            minChunks: Infinity,
            chunks: ['components', 'vendor']
        }),
    ]
}