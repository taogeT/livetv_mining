import Vue from 'vue'

const root_url = '/rest';

function transformUrl(url){
    return url.match(/^(https?:)?\//) ? root_url + url : url
}

export const SiteRes = new Vue.resource(transformUrl('/site{/id}{/subType}'))

export const ChannelRes = new Vue.resource(transformUrl('/channel{/id}{/subType}'))

export const RoomRes = new Vue.resource(transformUrl('/room{/id}'))

export const UserRes = new Vue.resource(transformUrl('/user{/subType}'))

export const SubscribeRes = new Vue.resource(transformUrl('/subscribe{/subType}{/id}'))
