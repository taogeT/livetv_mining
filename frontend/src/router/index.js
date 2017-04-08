import VueRouter from 'vue-router'
import RoomRank from 'views/room/Rank.vue'
import RoomDetail from 'views/room/Detail.vue'
import ChannelRank from 'views/channel/Rank.vue'
import ChannelDetail from 'views/channel/Detail.vue'
import Site from 'views/Site.vue'
import Search from 'views/Search.vue'
import Subscribe from 'views/Subscribe.vue'
import Login from 'views/Login.vue'
import About from '../../../README.md'
import store from 'store'

const router = new VueRouter({
    mode: 'history',
    scrollBehavior: () => ({ y: 0 }),
    routes: [
        { path: '/room/:id(\\d+)?', component: RoomDetail, name: 'room' },
        { path: '/room/rank', component: RoomRank, name: 'roomrank' },
        { path: '/channel/:id(\\d+)?', component: ChannelDetail, name: 'channel' },
        { path: '/channel/rank', component: ChannelRank, name: 'channelrank' },
        { path: '/site/:id(\\d+)?', component: Site, name: 'site' },
        { path: '/search', component: Search, name: 'search' },
        { path: '/subscribe', component: Subscribe, name: 'subscribe', meta: { auth: true } },
        { path: '/login', component: Login, name: 'login' },
        { path: '/about', component: About, name: 'about' },
        { path: '/', component: RoomRank, name: 'index' },
        { path: '*', redirect: { name: 'index' } }
    ]
})

router.beforeEach((to, from, next) => {
    if(to.meta.auth){
        store.dispatch('verify').then((v) => {
            if(v){
                next()
            }else{
                next({ path: '/login?next=' + to.path })
            }
        })
    }else{
        next()
    }
})

export default router
