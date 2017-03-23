<template>
  <div style="text-align: center;">
    <router-link :to="{ name: 'site', params: { id: site.id } }">
      <img height="100px" width="250px" :src="site.image">
    </router-link>
    <h4>
      <p>
        {{ site.name }}
        <router-link :to="{ name: 'site', params: { id: site.id } }">更多内容</router-link>
      </p>
    </h4>
  </div>
</template>

<script>
export default {
  name: 'site-header',
  props: ['site']
}
</script>