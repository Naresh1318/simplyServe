/**
 * Insert HTML in the desired id and evaluate scripts
 * @param id, id to insert text in
 * @param text, HTML text to insert (evaluates content inside scripts)
 */
function insertAndExecute(id, text) {
    document.getElementById(id).innerHTML = text;
    var scripts = Array.prototype.slice.call(document.getElementById(id).getElementsByTagName("script"));
    for (var i = 0; i < scripts.length; i++) {
        if (scripts[i].src != "") {
            var tag = document.createElement("script");
            tag.src = scripts[i].src;
            document.getElementsByTagName("head")[0].appendChild(tag);
        }
        else {
            eval(scripts[i].innerHTML);
        }
    }
}

// Upload button
const upload_btn = document.getElementById("file")
const upload_text = document.getElementById("upload_text")

upload_btn.addEventListener("change", function() {
    if (upload_btn.value) {
        upload_text.innerText = upload_btn.value.match(
          /[\/\\]([\w\d\s\.\-\(\)]+)$/
        )[1]
    } else {
        upload_text.innerText = "No file chosen, yet.";
    }
})

let app = new Vue({
    el: "#app",
    vuetify: new Vuetify(),
    data: {
        pages: [{title: "Home", icon: "folder", show: true},
                {title: "Public", icon: "public", show: false},
                {title: "Admin", icon: "gavel", show: false}],
        current_page: page,
        index_html_file: ".index.html",
        username: "",
        server_name: "",
        admin: false,
        default_dir: "",
        current_dir: "",
        all_items: [],
        current_dirs: [],
        current_files: [],
        current_file_sizes: [],
        file_manager_header: [{text: "Name", align: "left", sortable: true, value: "name"},
                              {text: "File size", align: "left", sortable: false, value: "size"}],
        item_search: "",
        selected: [],
        navigation_stack: [],
        disable_back: true,
        loading_status: false,
        show_alert: false,
        alert_status: "",
        admin_users_list: [],
        admin_users_header: [{text: "Email", align: "left", sorted: true, value: "email"},
                             {text: "Username", value: "username"},
                             {text: "Actions", value: "action", sortable: false }],
        admin_add_user_default: {username: "", email: "", password: ""},
        admin_add_user_dialog: false
    },
    methods: {
        /**
        * Gets and sets the default home directory. Also, check if current user is the admin
        */
        home_page_setup: function() {
            axios.get("/default_dir")
            .then(function (response) {
                app.default_dir = response["data"]["default_dir"]
                app.current_dir = app.default_dir
            })
            .catch(function(error) {
                console.log("ERROR: " + error)
            })
            .then(function() {
                app.is_admin()
                app.list_dir(app.current_dir)
                app.get_username()
            })
        },
        upload_page_setup: function() {
            app.default_dir = "."
            app.current_dir = "."
            app.list_dir(app.current_dir)
        },
        admin_page_setup: function() {
            app.list_users()
        },
        /**
        * Retrieves and sets current_dirs and current_files variables. Index files rendering function is called
        * after obtaining the current files in the directory.
        * @param {string} path, path to retrieve and list files/dirs from
        */
        list_dir: function(path) {
            let ls_route
            if (app.current_page === "Home") {
                ls_route = "/ls"
            } else if (app.current_page === "Public") {
                ls_route = "/uploads_ls"
            }
            return axios.get(ls_route, {
                    params: {
                    "path": path
                    }
               })
                .then(function (response) {
                    app.current_dirs = response["data"]["dirs"]
                    app.current_files = response["data"]["files"]
                    app.all_items = []
                    app.all_items = app.all_items.concat(app.current_dirs, app.current_files)

                    if (app.current_page === "Home") {
                        app.render_index();  // Render index file if present
                    }
                    else if (app.current_page === "Public") {
                        for (let i=0; i < app.all_items.length; i++) {
                            if (app.all_items[i].is_file) {
                                if (app.current_dir === ".") {
                                    let split_url = document.URL.split("/")
                                    app.all_items[i]["link"] = `${split_url[0]}//` + split_url[2]
                                        + `/public/${app.current_dir.slice(1, app.current_dir.length)}` + app.all_items[i]["name"]
                                }
                                else {
                                    let split_url = document.URL.split("/")
                                    app.all_items[i]["link"] = `${split_url[0]}//` + split_url[2]
                                        + `/public${app.current_dir.slice(1, app.current_dir.length)}/` + app.all_items[i]["name"]
                                    }
                            }
                        }
                    }
                })
                .catch(function(error) {
                    console.log("ERROR: " + error)
                })
        },
        upload_file_selector: function() {
            upload_btn.click()
        },
        upload: function() {
            let formData = new FormData();
            // let file = document.querySelector("#file");
            for (let i=0; i<upload_btn.files.length; i++) {
                formData.append(upload_btn.files[i].name, upload_btn.files[i]);
            }
            app.loading_status = true
            axios.post(app.get_upload_url(), formData, {
                headers: {
                  "Content-Type": "multipart/form-data"
                }
            }).then((response) => {
                app.loading_status = false
                if (response.data.INFO) {
                    // Write status to snicker bar
                    app.alert_status = response.data.INFO
                    // Reload page after upload
                    app.navigate_to(app.current_dir, true)
                } else {
                    // Write status to snicker bar
                    app.alert_status = response.data.ERROR
                }
                app.show_alert = true
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
                app.current_dir = dir
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
        /**
         * Copy text to clipboard
         * @param text, text to copy
         */
        copy_to_clipboard: function (text) {
            let dummy = document.createElement("textarea")
            document.body.appendChild(dummy)
            dummy.value = text
            dummy.select()
            document.execCommand("copy")
            document.body.removeChild(dummy)
            app.alert_status = "Copied to clipboard!"
            app.show_alert = true
        },
        /**
         * Returns relative path from linked_dir using the absolute path
         */
        get_relative_path: function(directory) {
            return this.current_dir.split("linked_dir")[1]
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
                        insertAndExecute("index_viewer", response["data"])
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
                    app.pages[1].show = app.admin
                    app.pages[2].show = app.admin
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
        },
        change_page: function (page) {
            app.current_page = page
            if (app.current_page === "Home") {
                app.home_page_setup()
            } else if (app.current_page === "Public") {
                app.upload_page_setup()
            } else if (app.current_page === "Admin") {
                app.admin_page_setup()
            }
        },
        get_upload_url: function() {
          return `/public_uploads?folder=${this.current_dir}`
        },
        /**
         * Get a list of all users in the database
         * Use this function to update users list when needed
         */
        list_users: function() {
            axios.get("/list_users")
                .then(function(response) {
                    app.admin_users_list = response["data"]["users_list"]
                })
        },
        admin_close_dialog: function() {
            this.admin_add_user_dialog = false
            setTimeout(() => {
                this.admin_add_user_default = {username: "", email: "", password: ""}
            }, 300)
        },
        admin_save_dialog: function () {
            if (app.admin_add_user_default.email.length < 1 || app.admin_add_user_default.username.length < 1
                || app.admin_add_user_default.password.length < 1) {
                app.alert_status = "Invalid Input"
                app.show_alert = true
                return
            }

            axios.post("add_user",
                {
                    "username": app.admin_add_user_default.username,
                    "email": app.admin_add_user_default.email,
                    "password": app.admin_add_user_default.password
                })
                .then(function(response) {
                    if (response["data"]["user_added"]) {
                        app.admin_add_user_default = {username: "", email: "", password: ""}
                        app.alert_status = "User added!"
                    }
                    else {
                        app.alert_status = "Email taken or invalid input :("
                    }
                    app.show_alert = true
                    app.admin_page_setup()
                })
        },
        admin_delete_user: function(email) {
            axios.post("delete_user",
                {
                    "email": email
                }).then(function(response) {
                    if (response["data"]["user_deleted"]) {
                        app.alert_status = "User deleted!"
                    }
                    else {
                        app.alert_status = "User not found :( or admin cannot be deleted"
                    }
                    app.show_alert = true
                    app.admin_page_setup()
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
        this.home_page_setup()
    }
})
