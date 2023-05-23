<template>
  <div class="d-flex align-center justify-space-between my-6">
    <div class="mr-10">
      <div class="text-h5">{{ name }}</div>
      <div class="text-body-1">{{ description }}</div>
    </div>
    <slot />
  </div>
</template>

<script>
export default {
  name: "SettingsLayout",
  props: {
    name: { type: String },
    description: { type: String }
  }
};
</script>
