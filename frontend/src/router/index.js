import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import RoomRank from '../views/room/Rank.vue'
import RoomDetail from '../views/room/Detail.vue'
import ChannelRank from '../views/channel/Rank.vue'
import ChannelDetail from '../views/channel/Detail.vue'
import Site from '../views/Site.vue'
import Search from '../views/Search.vue'
import Login from '../views/Login.vue'
import About from '../../README.md'

export default new VueRouter({
    mode: 'history',
    scrollBehavior: () => ({ y: 0 }),
    routes: [
        { path: '/room/:id(\\d+)?', component: RoomDetail, name: 'room' },
        { path: '/room/rank', component: RoomRank, name: 'roomrank' },
        { path: '/channel/:id(\\d+)?', component: ChannelDetail, name: 'channel' },
        { path: '/channel/rank', component: ChannelRank, name: 'channelrank' },
        { path: '/site/:id(\\d+)?', component: Site, name: 'site' },
        { path: '/search', component: Search, name: 'search' },
        { path: '/login', component: Login, name: 'login' },
        { path: '/about', component: About, name: 'about' },
        { path: '/', component: RoomRank, name: 'index' }
    ]
})
