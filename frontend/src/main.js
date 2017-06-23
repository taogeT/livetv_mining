import Vue from 'vue'
import router from 'router'
import store from 'store'
import * as filters from 'filters'
import App from './App'
import 'css/styles.css'

Object.keys(filters).forEach(key => {
    Vue.filter(key, filters[key])
})

new Vue({
    router,
    store,
    el: '#app',
    render: h => h(App)
})
