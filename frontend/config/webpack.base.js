const path = require('path')
const dirname = path.join(__dirname, '..')

module.exports = {
    entry: path.join(dirname, 'src', 'main'),
    output: {
        path: path.join(dirname, 'dist'),
        filename: '[name].[hash:7].js',
        chunkFilename: '[id].[chunkhash:7].js'
    },
    module: {
        loaders: [
            { test: /\.js$/, exclude: /node_modules/, loader: 'babel' },
            { test: /\.vue$/, loader: 'vue' },
            { test: /\.md$/, loader: 'vue-markdown' }
        ]
    },
    resolve: {
        extensions: ['', '.js', '.vue', '.json'],
        fallback: [path.join(dirname, 'node_modules')],
        alias: {
            components: path.resolve(dirname, 'src', 'components'),
            filters: path.resolve(dirname, 'src', 'filters'),
            resource: path.resolve(dirname, 'src', 'resource'),
            router: path.resolve(dirname, 'src', 'router'),
            store: path.resolve(dirname, 'src', 'store'),
            views: path.resolve(dirname, 'src', 'views')
        }
    },
    resolveLoader: {
        fallback: [path.join(dirname, 'node_modules')]
    },
    externals: {
        'jquery': 'jQuery',
        'vue': 'Vue',
        'vue-router': 'VueRouter',
        'vuex': 'Vuex',
        'vue-resource': 'VueResource',
        'moment': 'moment'
    }
}