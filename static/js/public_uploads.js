let vue_upload = new Vue({
    el: "#app",
    data: {
        username: "",
        server_name: "",
        admin: false,
        files: []
    },
    methods: {
        /**
         * Notify on successful upload
         */
        successUpload: function () {
            this.$vs.notify({color: "dark", title: "Upload Success"})
            this.reload()
        },
        /**
         * Reload files in public directory
         */
        reload: function () {
            axios.get("/uploads_ls")
            .then(function(response) {
                vue_upload.files = response["data"]["files"]
                for (let file of vue_upload.files) {
                    file["link"] = document.URL.split("/")[2] + "/public/" + file["name"]
                }
            })
        },
        /**
         * Copy text to clipboard
         * @param text, text to copy
         */
        copy_to_clipboard: function (text) {
            var dummy = document.createElement("textarea")
            document.body.appendChild(dummy)
            dummy.value = text
            dummy.select()
            document.execCommand("copy")
            document.body.removeChild(dummy)
            this.$vs.notify({color: "dark", title: "Copied to clipboard"})
        },
        /**
         * Check if current user is admin
         */
        is_admin: function() {
            axios("/is_admin")
                .then(function(response) {
                    vue_upload.admin = response["data"]["admin"]
                })
        },
        /**
         * Get and set username
         */
        get_username: function() {
            axios("/get_username")
                .then(function (response) {
                    vue_upload.username = response["data"]["username"]
                })
        }
    },
    created: function () {
        // Get server name
        axios.get("/server_name")
            .then(function(response) {
                vue_upload.server_name = response["data"]["server_name"]
            })
        this.is_admin()
        this.get_username()
        this.reload()
    }
})
