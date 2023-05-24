<template>
  <v-btn
      :icon="`mdi-file-image-${file ? 'remove' : 'plus'}-outline`"
      @click="clickOnIconButton"
      :disabled="isSaving"
      :loading="isSaving"
      :title="file ? 'Supprimer l\'image' : 'Uploader une image'"
  />
  <input
      tabindex="-1"
      type="file"
      @change="fileChange"
      accept="image/jpeg, image/png, image/gif"
      class="d-none"
      ref="fileInput"
  />
  <span class="text-body-1 ml-4">{{ file ? file.name : 'Aucune image sélectionnée' }}</span>
</template>

<script>
export default {
  name: "ImageUpload",
  emits: [ "file-change" ],
  data() {
    return {
      isSaving: false,
      fileReader: null,
      fileInput: null,
      file: null
    };
  },
  mounted() {
    this.fileInput = this.$refs.fileInput;
    this.fileReader = new FileReader();
    this.fileReader.addEventListener(
        "load",
        () => {
          // fileReader holds a b64 string of the image
          const fileDataUrl = this.fileReader?.result;
          this.isSaving = false;
          this.$emit("file-change", fileDataUrl);
        },
        false
    );
  },
  methods: {
    fileChange(event) {
      this.isSaving = true;
      const input = event.target;
      // pick the first file uploaded
      this.file = input.files[0];
      // feed the file to the asynchronous file reader
      // (next step is in the load eventListener defined in mounted)
      this.fileReader.readAsDataURL(this.file);
    },
    clickOnIconButton() {
      if (this.file) {
        this.file = null;
        this.$emit("file-change", "");
        if (this.fileInput)
          this.fileInput.value = "";
      } else
        this.$refs.fileInput.click();
    }
  }
};
</script>
