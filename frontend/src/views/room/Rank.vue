<template>
  <div class="room-rank">
    <div class="container">
      <div class="row">
        <template v-for="item in site">
          <div class="col-lg-4" style="text-align: center;">
            <site-header :site="item"></site-header>
            <span style="text-align: left;">
              <h3>房间人气 TOP{{ rank_num }}</h3>
              <table class="table table-striped">
                <thead>
                  <th width="50px">排名</th>
                  <th>房间</th>
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
                    <td>{{ roomitem.online }}</td>
                  </tr>
                </tbody>
              </table>
            </span>
          </div>
        </template>
      </div>
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
      rank_num: 10
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