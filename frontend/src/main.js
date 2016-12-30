import Vue from 'vue'
import router from './router'
import * as filters from './filters'
import App from './App'

Vue.config.debug = true

Object.keys(filters).forEach(key => {
    Vue.filter(key, filters[key])
})

new Vue({
    router,
    el: '#app',
    render: h => h(App)
})
