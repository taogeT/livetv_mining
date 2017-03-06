<template>
  <div class="room-rank">
    <div class="container">
      <template v-for="n_item in Math.ceil(site.length / columnnum)">
        <div class="row" style="text-align: center;">
          <div v-for="item in site.slice((n_item - 1) * columnnum, n_item * columnnum)" class="col-lg-6 col-md-6">
            <site-header :site="item"></site-header>
            <span style="text-align: left;">
              <h3>房间人气 TOP{{ rank_num }}</h3>
              <table class="table table-striped">
                <thead>
                  <th width="50px">排名</th>
                  <th>房间</th>
                  <th>频道</th>
                  <th>人气</th>
                </thead>
                <tbody>
                  <tr v-for="(roomitem, index) in item.rooms">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <router-link :to="{ name: 'room', params: { id: roomitem.id } }">
                        {{ roomitem.name }}
                      </router-link><br>
                      <router-link :to="{ name: 'room', params: { id: roomitem.id } }" v-if="index < 3">
                        <img width="250px" height="150px" :src="roomitem.image">
                      </router-link>
                    </td>
                    <td>
                      <router-link :to="{ name: 'channel', params: { id: roomitem.channel_id } }">
                        {{ roomitem.channel }}
                      </router-link>
                    </td>
                    <td>{{ roomitem.online }}</td>
                  </tr>
                </tbody>
              </table>
            </span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import SiteHeader from 'components/SiteHeader.vue'
import { SiteRes } from 'resource'

export default {
  name: 'room-rank',
  data () {
    return {
      site: [],
      rank_num: 10,
      columnnum: 2
    }
  },
  components: { SiteHeader },
  mounted () {
    SiteRes.query().then(
      (response) => {
        this.site = response.body
        for(const index in this.site){
          this.get_site_rooms(index)
        }
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  },
  methods: {
    get_site_rooms (index) {
      SiteRes.query({ id: this.site[index].id, subType: 'room', per_page: this.rank_num }).then(
        (resp) => {
          this.$set(this.site[index], 'rooms', resp.body)
        }, (resp) => {
          console.log(resp.body['message'])
        }
      )
    }
  }
}
</script>