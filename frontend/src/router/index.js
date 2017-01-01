import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const RoomRank = resolve => {
    require.ensure(['../views/room/Rank.vue'], () => {
        resolve(require('../views/room/Rank.vue'))
        })
}
const RoomDetail = resolve => {
    require.ensure(['../views/room/Detail.vue'], () => {
        resolve(require('../views/room/Detail.vue'))
    })
}

const ChannelRank = resolve => {
    require.ensure(['../views/channel/Rank.vue'], () => {
        resolve(require('../views/channel/Rank.vue'))
    })
}
const ChannelDetail = resolve => {
    require.ensure(['../views/channel/Detail.vue'], () => {
        resolve(require('../views/channel/Detail.vue'))
    })
}

const Site = resolve => {
    require.ensure(['../views/Site.vue'], () => {
        resolve(require('../views/Site.vue'))
    })
}

const Search = resolve => {
    require.ensure(['../views/Search.vue'], () => {
        resolve(require('../views/Search.vue'))
    })
}

const Login = resolve => {
    require.ensure(['../views/Login.vue'], () => {
        resolve(require('../views/Login.vue'))
    })
}

const About = resolve => {
    require.ensure(['../../README.md'], () => {
        resolve(require('../../README.md'))
    })
}

export default new VueRouter({
  //mode: 'history',
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
