<template>
  <div class="subscribe">
    <div class="page-header">
      <p><h3>已订阅房间<small>（{{ subscribe_count }}/{{ subscribe_max }}）</small></h3></p>
    </div>

    <form class="form form-inline" role="form" onsubmit="return false">
      <div class="form-group required">
        <label for="roomurl">房间URL</label>
        <input class="form-control" size="40" type="text" v-model="roomurl">
      </div>
      <button class="btn btn-primary" v-on:click="submit" >订阅</button>
    </form>

    <template v-for="(roomitems, roomkey) in rooms">
      <h4>{{ roomkey }}</h4>
      <template v-if="roomitems" v-for="room in roomitems">
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
              <button class="btn btn-danger" v-on:click="cancel">取消订阅</button>
            </p>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script>
export default {
  name: 'subscribe',
  data () {
    return {
      rooms: {},
      subscribe_count: 0,
      subscribe_max: 0
    }
  },
  method: {
    submit () {
      console.log('submit')
    },
    cancel () {
      console.log('cancel')
    }
  }
}
</script>