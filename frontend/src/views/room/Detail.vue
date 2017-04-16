<template>
  <div class="room-detail">
    <div class="row">
      <div v-if="room.image" class="col-lg-4 col-md-4">
        <img class="img-rounded" width="90%" :src="room.image">
      </div>
      <div :class="room.image ? 'col-lg-8 col-md-8' : 'col-lg-12 col-md-12'" style="text-align: left;">
        <h2>{{ room.name }}<small><a :href="room.url" target="_blank">官网</a></small></h2>
        <p>
          <h4>主播：{{ room.host }}</h4>
          <h4>
            频道：<router-link :to="{ name: 'channel', params: { id: room.channel_id }}">{{ room.channel }}</router-link>
            &nbsp;&nbsp;&nbsp;&nbsp;
            站点：<router-link :to="{ name: 'site', params: { id: room.site_id }}">{{ room.site }}</router-link>
          </h4>
          <h4>
            状态：{{ room.opened ? '正在直播': '未直播' }}
            &nbsp;&nbsp;&nbsp;&nbsp;
            更新时间：{{ room.crawl_date | moment }}
          </h4>
          <h4>观看人气：{{ room.online }}</h4>
          <h4 v-if="room.followers > 0">关注数：{{ room.followers }}</h4>
          <h4 v-if="room.announcement">公告：<pre>{{ room.announcement }}</pre></h4>
          <h4 v-if="room.description">描述：<pre>{{ room.description }}</pre></h4>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { RoomRes } from 'resource'

export default {
  name: 'room-detail',
  data () {
    return { room: {} }
  },
  mounted () {
    RoomRes.query({ id: this.$route.params.id }).then(
      (response) => {
        this.room = response.body
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  }
}
</script>