<template>
  <div class="site-header">
    <router-link :to="{ name: 'site', params: { id: site.id } }">
      <img height="100px" :src="site.image">
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