<template>
  <BlobCursor
    blobType="circle"
    fillColor="#27FF64"
    :trailCount="3"
    :sizes="[60, 125, 75]"
    :innerSizes="[20, 35, 25]"
    innerColor="rgba(255,255,255,0.8)"
    :opacities="[0.6, 0.6, 0.6]"
    shadowColor="rgba(0,0,0,0.75)"
    :shadow-Blur="5"
    :shadowOffsetX="10"
    :shadowOffsetY="10"
    :filterDtdDeviation="30"
    :useFilter="true"
    :fastDuration="0.1"
    :slowDuration="0.5"
    :zIndex="100"
  />
</template>

<script setup lang="ts">
  import BlobCursor from "./BlobCursor.vue";
</script>