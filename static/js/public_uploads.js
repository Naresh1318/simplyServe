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
                    file["link"] = document.URL.split("/")[2] + "/public/" + file["name"]
                }
            })
        },
        copy_to_clipboard: function (text) {
            var dummy = document.createElement("textarea")
            document.body.appendChild(dummy)
            dummy.value = text
            dummy.select()
            document.execCommand("copy")
            document.body.removeChild(dummy)
            this.$vs.notify({color: "dark", title: "Copied to clipboard"})
        }
    },
    created: function () {
        this.reload()
    }
})
