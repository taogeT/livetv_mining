<template>
  <div class="room-rank">
    <div class="container">
      <div class="row">

        <!-- Nav tabs -->
        <div class="col-md-2">
          <ul class="nav nav-pills nav-stacked affix" role="tablist">
            <li role="presentation" v-for="(site_item, site_index) in site" :class="{ active: site_index == 0}">
              <a :href="'#' + site_item.code" :aria-controls="site_item.code" role="tab" data-toggle="tab">
                <img height="50px" :src="site_item.image">
              </a>
            </li>
          </ul>
        </div>

        <!-- Tab panes -->
        <div class="col-md-10">
          <div class="tab-content" style="margin-left: 30px;">
            <div role="tabpanel" class="tab-pane" v-for="(item, site_index) in site"
              :class="{ active: site_index == 0}" :id="item.code">
              <site-header :site="item"></site-header>
              <span style="text-align: left;">
                <h3>房间人气 TOP{{ rank_num }}</h3>
                <table class="table table-striped">
                  <thead>
                    <th width="50px">排名</th>
                    <th>房间</th>
                    <th>主持</th>
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
                      <td>{{ roomitem.host }}</td>
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
        </div>

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
      rank_num: 20
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