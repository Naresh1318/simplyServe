let vue_upload = new Vue({
    el: "#app",
    data: {
        username: "",
        server_name: "",
        admin: false,
        default_dir: "",
        current_dir: "",
        current_dirs: [],
        files: [],
        navigation_stack: [],
        disable_back: true
    },
    methods: {
        /**
         * Notify on successful upload
         */
        successUpload: function () {
            this.$vs.notify({color: "dark", title: "Upload Success"})
            this.reload(this.current_dir)
        },
        /**
         * Reload files in public directory
         */
        reload: function (dir) {
            axios.get("/uploads_ls", {
                params: {
                    path: dir
                }
            })
            .then(function(response) {
                vue_upload.current_dirs = response["data"]["dirs"]
                vue_upload.files = response["data"]["files"]
                for (let file of vue_upload.files) {
                    if (dir === ".")
                        file["link"] = document.URL.split("/")[2] + `/public/${dir.slice(1, dir.length)}` + file["name"]
                    else
                        file["link"] = document.URL.split("/")[2] + `/public${dir.slice(1, dir.length)}/` + file["name"]
                }
            })
        },
        /**
         * Sets current_dir to the previous dir and updates navigation_stack
         */
        navigate_back: function() {
            vue_upload.current_dir = vue_upload.navigation_stack.pop()
            vue_upload.reload(this.current_dir)
            if (vue_upload.navigation_stack.length < 1)
                vue_upload.disable_back = true
        },
        /**
         * Sets current_dir to the required dir and updates navigation_stack
         * @param {string} dir, directory to navigate to
         * @param {boolean} abs_path, true  -> dir is an absolute path
         *                            false -> dir is relative to current_dir
         */
        navigate_to: function(dir, abs_path=false) {
            vue_upload.navigation_stack.push(vue_upload.current_dir)
            if (abs_path)
                vue_upload.current_dir = vue_upload.default_dir
            else
                vue_upload.current_dir = vue_upload.current_dir + "/" + dir
            vue_upload.reload(this.current_dir)
            if (vue_upload.navigation_stack.length > 0)
                vue_upload.disable_back = false
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
        this.default_dir = "."
        this.current_dir = this.default_dir
        // Get server name
        axios.get("/server_name")
            .then(function(response) {
                this.server_name = response["data"]["server_name"]
            })
        this.is_admin()
        this.get_username()
        this.reload(this.current_dir)
    }
})
