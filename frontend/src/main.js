import Vue from 'vue'
import VueResource from 'vue-resource'
import router from 'router'
import store from 'store'
import * as filters from 'filters'
import App from './App'

Object.keys(filters).forEach(key => {
    Vue.filter(key, filters[key])
})

new Vue({
    router,
    store,
    el: '#app',
    render: h => h(App)
})
