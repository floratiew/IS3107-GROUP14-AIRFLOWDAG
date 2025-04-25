<template>
    <div>
        <h2>School Clusters Map</h2>
        <div class="iframe-container">
            <iframe
                src="/school_clusters_map.html"
                class="responsive-iframe"
                allowfullscreen
                style="border:none;" 
            ></iframe>
        </div>
    </div>
</template>

<style scoped>
.iframe-container {
  position: relative;
  overflow: hidden;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
}

.responsive-iframe {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  width: 100%;
  height: 100%;
  border: none;
}
</style>