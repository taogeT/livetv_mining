<template>
  <div class="subscribe">
    <div class="page-header">
      <p>
        <h3>已订阅房间
          <small>（{{ subscribeCount }}/{{ this.$store.state.user.subscription }}）</small>
        </h3>
      </p>
    </div>

    <div class="alert alert-danger alert-dismissible" role="alert" v-if="errorMsg != ''">
      <button type="button" class="close" data-dismiss="alert">
        <span aria-hidden="true">&times;</span>
        <span class="sr-only">Close</span>
      </button>
      {{ errorMsg }}
    </div>

    <form class="form form-inline" role="form" onsubmit="return false">
      <div class="form-group required">
        <input class="form-control" size="40" type="text" v-model="roomUrl" placeholder="房间官网URL">
      </div>
      <button class="btn btn-primary" :disabled="roomUrl == ''" v-on:click="add" >订阅</button>
    </form>
    <hr>

    <template v-for="(roomitems, roomkey) in rooms">
      <h3 v-if="roomitems.length > 0">{{ roomkey }}</h3>
      <template v-for="(room, roomindex) in roomitems">
        <div class="row">
          <div class="col-lg-4 col-md-5">
            <img v-if="room.image" class="img-rounded" width="100%" :src="room.image" :title="room.name">
          </div>
          <div class="col-lg-8 col-md-7" style="text-align: left;">
            <h3>
              <router-link :to="{ name: 'room', params: { id: room.id} }">{{ room.name }}</router-link>
              <small>
                <span v-if="room.opened" class="label label-success">直播中</span>
                <span v-else class="label label-danger">未直播</span>
              </small>
            </h3>
            <p>
              <h4>官网：<a :href="room.url" target="_blank">{{ room.url }}</a></h4>
              <h4>
                主播：{{ room.host }}
                &nbsp;&nbsp;频道：<router-link :to="{ name: 'channel', params: { id: room.channel_id } }">{{ room.channel }}</router-link>
                &nbsp;&nbsp;站点：<router-link :to="{ name: 'site', params: { id: room.site_id } }">{{ room.site }}</router-link>
              </h4>
              <button class="btn btn-danger" v-on:click="cancel(room.id, roomindex, roomkey)">取消订阅</button>
            </p>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script>
import { SubscribeRes } from 'resource'

export default {
  name: 'subscribe',
  data () {
    return {
      rooms: {},
      subscribeCount: 0,
      roomUrl: '',
      errorMsg: ''
    }
  },
  mounted () {
    SubscribeRes.query({ subType: 'room' }).then(
      (resp) => {
        for(var rindex in resp.body){
          var roomobj = resp.body[rindex]
          if(this.rooms[roomobj.site]){
            this.rooms[roomobj.site].push(roomobj)
          }else{
            this.$set(this.rooms, roomobj.site, [roomobj])
          }
          this.subscribeCount += 1
        }
      }, (resp) => {
        console.log(resp.body['message'])
      }
    )
  },
  methods: {
    add () {
      this.errorMsg = ''
      SubscribeRes.save({ subType: 'room' }, { url: this.roomUrl }).then(
        (resp) => {
          this.roomUrl = ''
          var roomobj = resp.body
          if(this.rooms[roomobj.site]){
            this.rooms[roomobj.site].push(roomobj)
          }else{
            this.$set(this.rooms, roomobj.site, [roomobj])
          }
        }, (resp) => {
          this.errorMsg = resp.body['message']
        }
      )
    },
    cancel (roomid, roomindex, roomkey) {
      this.errorMsg = ''
      SubscribeRes.delete({ subType: 'room', id: roomid }).then(
        (resp) => {
          this.rooms[roomkey].splice(roomindex, 1)
        }, (resp) => {
          this.errorMsg = resp.body['message']
        }
      )
    }
  }
}
</script>