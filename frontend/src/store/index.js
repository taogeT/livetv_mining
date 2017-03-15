import Vue from 'vue'
import Vuex from 'vuex'
import { UserRes } from 'resource'

const store = new Vuex.Store({
    state: {
        user: null
    },
    mutations: {
        modifyUser (state, userobj) {
            state.user = userobj
        }
    },
    actions: {
        verify (context) {
            return UserRes.query({ subType: 'verify'}).then(
                (resp) => {
                    if(context.state.user == null || context.state.user.username != resp.username){
                        return UserRes.query().then(
                            (resp) => {
                                context.commit('modifyUser', resp.body)
                                return true
                            }, (resp) => {
                                return false
                            }
                        )
                    }
                    return true
                }, (resp) => {
                    context.commit('modifyUser', null)
                    return false
                }
            )
        }
    }
})

export default store
