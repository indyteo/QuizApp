<template>
  <div class="pa-10 d-flex flex-column justify-center align-center h-100">
    <div style="min-width: 300px">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: "CenterLayout"
};
</script>
