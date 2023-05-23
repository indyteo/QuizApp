<template>
  <v-dialog v-model="dialog" width="444">
    <template v-slot:activator="{ props }">
      <slot :props="props" />
    </template>
    <v-card rounded="xl" class="pa-2">
      <v-card-text>
        <div v-if="definitive" class="text-center mt-2 mb-6">
          <v-icon icon="mdi-alert-outline" size="large" />
        </div>
        Êtes-vous sûr de vouloir {{ action }} ?
        <div v-if="definitive" class="text-red">Cette action est irréversible !</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="cancel">Annuler</v-btn>
        <v-btn @click="confirm" :color="definitive ? 'error' : 'primary'">Confirmer</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "ConfirmationDialog",
  props: {
    action: { type: String },
    definitive: { type: Boolean }
  },
  data () {
    return {
      dialog: false
    };
  },
  methods: {
    cancel() {
      this.dialog = false;
      this.$emit("cancel");
    },
    confirm() {
      this.dialog = false;
      this.$emit("confirm");
    }
  },
  emits: [ "cancel", "confirm" ]
};
</script>
