<template>
  <div class="room-list">
    <template v-for="n_item in Math.ceil(rooms.length / columnnum)">
      <div class="row" style="text-align: center;">
        <div v-for="item in rooms.slice((n_item - 1) * columnnum, n_item * columnnum)" class="col-lg-3 col-md-6">
          <router-link v-if="item.image" :to="{ name: 'room', params: { id: item.id } }" :title="item.name">
            <img class="img-rounded" width="100%" :src="item.image">
          </router-link>
          <router-link :to="{ name: 'room', params: { id: item.id } }" :title="item.name">
            {{ item.name | except 34 }}
          </router-link>
          <p>
            主播 {{ item.host }}<br>
            人气 {{ item.online }}&nbsp;{{ item.crawl_date | moment }} 更新
          </p>
        </div>
      </div>
    </template>
    <pagination :current-page="pagination.current_page" :total-page="pagination.last_page" v-on:seek="seekPage"></pagination>
  </div>
</template>

<script>
import Pagination from './Pagination.vue'

export default {
  name: 'room-list',
  props: ['channelId'],
  components: { Pagination },
  data () {
    return { rooms: [], pagination: {}, columnnum: 4 }
  },
  methods: {
    seekPage (pageNum) {
      this.$http.get('http://localhost:5000/rest/channel/' + this.channelId + '/room?isvue=1&page=' + pageNum).then(
        (response) => {
          this.rooms = response.body.data
          this.pagination = Object.assign({}, this.pagination, response.body.pagination)
        }, (response) => {
          console.log(response.body['message'])
        }
      )
    }
  },
  mounted () {
    this.seekPage(1)
  }
}
</script>
