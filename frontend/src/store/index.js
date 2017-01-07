import Vue from 'vue'
import Vuex from 'vuex'
import { AuthRes } from '../resource'

const store = new Vuex.Store({
    state: {
        user: null
    },
    getters: {
        isLogin (state) {
            return AuthRes.query({ subType: 'verify'}).then(
                (resp) => {
                    if(state.user == null || state.user.username != resp.username){
                        return AuthRes.query({ subType: 'user'}).then(
                            (resp) => {
                                state.user = resp
                                return true
                            }, (resp) => {
                                return false
                            }
                        )
                    }
                    return true
                }, (resp) => {
                    state.user = null
                    return false
                }
            )
        }
    }
})

export default store
