let vue_upload = new Vue({
    el: "#app",
    data: {
        files: []
    },
    methods: {
        successUpload: function () {
            this.$vs.notify({color: "success", title: "Upload Success"})
            this.reload()
        },
        reload: function () {
            axios.get("/uploads_ls")
            .then(function(response) {
                vue_upload.files = response["data"]["files"]
                for (let file of vue_upload.files) {
                    file["link"] = document.URL + "/" + file["name"]
                }
            })
        }
    },
    created: function () {
        this.reload()
    }
})
