let app = new Vue({
    el: "#app",
    data: {
        index_html_file: ".index.html",
        username: "",
        server_name: "",
        admin: false,
        default_dir: "",
        current_dir: "",
        current_dirs: [],
        current_files: [],
        current_file_sizes: [],
        selected: [],
        navigation_stack: [],
        disable_back: true
    },
    methods: {
        /**
        * Gets and sets the default home directory. Also, check if current user is the admin
        */
        initial_setup: function() {
            axios.get("/default_dir")
            .then(function (response) {
                app.default_dir = response["data"]["default_dir"]
                app.current_dir = app.default_dir
            })
            .catch(function(error) {
                console.log("ERROR: " + error)
            })
            .then(function() {
                app.list_dir(app.current_dir)
                app.is_admin()
                app.get_username()
            })
        },
        /**
        * Retrieves and sets current_dirs and current_files variables. Index files rendering function is called
        * after obtaining the current files in the directory.
        * @param {string} path path to retrieve and list files/dirs from
        */
        list_dir: function(path) {
            return axios.get("/ls", {
                        params: {
                        "path": path
                        }
                   })
                   .then(function (response) {
                        app.current_dirs = response["data"]["dirs"]
                        app.current_files = response["data"]["files"]
                        app.render_index();  // Render index file if present
                        return
                   })
                   .catch(function(error) {
                        console.log("ERROR: " + error)
                   })
        },
        /**
         * Sets current_dir to the previous dir and updates navigation_stack
         */
        navigate_back: function() {
            app.current_dir = app.navigation_stack.pop()
            app.list_dir(app.current_dir)
            if (app.navigation_stack.length < 1)
                app.disable_back = true
        },
        /**
         * Sets current_dir to the required dir and updates navigation_stack
         * @param {string} dir, directory to navigate to
         * @param {boolean} abs_path, true  -> dir is an absolute path
         *                            false -> dir is relative to current_dir
         */
        navigate_to: function(dir, abs_path=false) {
            app.navigation_stack.push(app.current_dir)
            if (abs_path)
                app.current_dir = app.default_dir
            else
                app.current_dir = app.current_dir + "/" + dir
            app.list_dir(app.current_dir)
            if (app.navigation_stack.length > 0)
                app.disable_back = false
        },
        /**
         * Returns link to the required file on the server
         * @param {string} file, file path relative to home/default directory
         */
        get_file_link: function(file) {
            return this.current_dir.split("simplyServe")[1] + "/"  + file
        },
        download_selected: function() {
            this.$vs.loading({type: "point", color: "#000000"})
            axios({
                    method: "post",
                    url: "/download_selected",
                    responseType: "blob",
                    data: {
                        "dir": app.current_dir,
                        "files": app.selected
                    }
                })
                .then((response) => {
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", "all_files.tar");
                    document.body.appendChild(link);
                    link.click();
                    this.$vs.loading.close()
                })
        },
        /**
         * Get and sets the render_index div to the contents of .index.html file in the current directory
         */
        render_index: function() {
            let l_current_files = []
            for (let file of this.current_files) {
                l_current_files.push(file.name)
            }
            let index_viewer = document.getElementById("index_viewer")
            if (l_current_files.includes(app.index_html_file)) {
                let file_link = this.get_file_link(app.index_html_file)
                axios.get(file_link,
                    {
                        params: {
                            "timestamp": Date.now()  // Prevent browser from using cached pages
                        }
                    })
                    .then(function(response) {
                        index_viewer.innerHTML = response["data"]
                    })
                    .catch(function (error) {
                        console.log("ERROR: " + error)
                    })
            }
            else {
                let message = `.index.html file not found in ${app.current_dir}`
                console.log("INFO: " + message)
                index_viewer.innerHTML = `<p> ${message} <p>`
            }
        },
        /**
         * Check if current user is admin
         */
        is_admin: function() {
            axios("/is_admin")
                .then(function(response) {
                    app.admin = response["data"]["admin"]
                })
        },
        /**
         * Get and set username
         */
        get_username: function() {
            axios("/get_username")
                .then(function (response) {
                    app.username = response["data"]["username"]
                })
        }
    },
    /**
     * Performs initial setup when the page is loaded
     */
    created: function() {
        // Get server name
        axios.get("/server_name")
            .then(function(response) {
                app.server_name = response["data"]["server_name"]
            })

        // Perform initial setup
        this.initial_setup()
    }
})
