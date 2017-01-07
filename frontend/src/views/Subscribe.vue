<template>
  <div class="subscribe">
    <div class="page-header">
      <p><h3>已订阅房间<small>（{{ subscribe_count }}/{{ this.$store.state.user.subscribe_max }}）</small></h3></p>
    </div>

    <div class="alert alert-warning alert-dismissible" role="alert" v-if="error_msg != ''">
      <button type="button" class="close" data-dismiss="alert">
        <span aria-hidden="true">&times;</span>
        <span class="sr-only">Close</span>
      </button>
      {{ error_msg }}
    </div>

    <form class="form form-inline" role="form" onsubmit="return false">
      <div class="form-group required">
        <label for="roomurl">房间URL</label>
        <input class="form-control" size="40" type="text" v-model="room_url">
      </div>
      <button class="btn btn-primary" :disabled="room_url != ''" v-on:click="add" >订阅</button>
    </form>

    <template v-for="(roomitems, roomkey) in rooms">
      <h4>{{ roomkey }}</h4>
      <template v-if="roomitems" v-for="(room, roomindex) in roomitems">
        <div class="row">
          <div class="col-lg-4 col-md-5">
            <img v-if="room.image_url" class="img-rounded" width="100%" :src="room.image_url" :title="room.name">
          </div>
          <div class="col-lg-8 col-md-7" style="text-align: left;">
            <h3>
              <router-link :to={ name: 'room', params: { id: room.id} }">{{ room.name }}</router-link>
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
import { SubscribeRes } from '../../resource'

export default {
  name: 'subscribe',
  data () {
    return {
      rooms: {},
      subscribe_count: 0,
      room_url: '',
      error_msg: ''
    }
  },
  mounted () {
    this.get_subscribe_list()
  },
  method: {
    get_subscribe_list () {
      SubscribeRes.query({ subType: 'room' }).then(
        (resp) => {
          this.rooms = Object.assign({}, this.rooms, resp.body.rooms)
          this.subscribe_count = resp.body.subscribe_count
        }, (resp) => {
          console.log(resp.body['message'])
        }
      )
    },
    add () {
      this.error_msg = ''
      SubscribeRes.save({ subType: 'room' }, { url: this.room_url }).then(
        (resp) => {
          if(this.rooms[resp.body['site']]){
            this.rooms[resp.body['site']].push(resp.body['room'])
          }else{
            this.rooms[resp.body['site']] = [resp.body['room']]
          }
        }, (resp) => {
          this.error_msg = resp.body['message']
        }
      )
    },
    cancel (room_id, roomindex, roomkey) {
      this.error_msg = ''
      SubscribeRes.delete({ subType: 'room' }, { room_id: room_id }).then(
        (resp) => {
          this.rooms[roomkey].splice(roomindex, 1)
        }, (resp) => {
          this.error_msg = resp.body['message']
        }
      )
    }
  }
}
</script>