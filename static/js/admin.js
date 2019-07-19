let vue_admin = new Vue({
    el: "#app",
    data: {
        username: "",
        server_name: "",
        admin: false,
        users_list: [],
        add_username: "",
        add_email: "",
        add_password: "",
        delete_email: "",
        log: "",
    },
    methods: {
        /**
         * Add user and update log
         */
        add_user: function() {
            if (vue_admin.add_email.length < 1 || vue_admin.add_username.length < 1 || vue_admin.add_password.length < 1) {
                vue_admin.log = "Invalid input"
                return
            }

            axios.post("add_user",
                {
                    "username": vue_admin.add_username,
                    "email": vue_admin.add_email,
                    "password": vue_admin.add_password
                })
                .then(function(response) {
                    if (response["data"]["user_added"]) {
                        vue_admin.add_username = ""
                        vue_admin.add_email = ""
                        vue_admin.add_password = ""
                        vue_admin.log = "User added!"
                    }
                    else {
                        vue_admin.log = "Email taken or invalid input :("
                    }
                    vue_admin.list_users()
                })
        },
        /**
         * Delete user and update log
         */
        delete_user: function() {
            axios.post("delete_user",
                {
                    "email": vue_admin.delete_email
                })
                .then(function(response) {
                    if (response["data"]["user_deleted"]) {
                        vue_admin.delete_email = ""
                        vue_admin.log = "User deleted"
                    }
                    else {
                        vue_admin.log = "User not found :( or admin cannot be deleted"
                    }
                    vue_admin.list_users()
                })
        },
        /**
         * Get a list of all users in the database
         * Use this function to update users list when needed
         */
        list_users: function() {
            axios.get("/list_users")
                .then(function(response) {
                    vue_admin.users_list = response["data"]["users_list"]
                })
        },
        /**
         * Check if current user is admin
         */
        is_admin: function() {
            axios("/is_admin")
                .then(function(response) {
                    vue_admin.admin = response["data"]["admin"]
                })
        },
        /**
         * Get and set username
         */
        get_username: function() {
            axios("/get_username")
                .then(function (response) {
                    vue_admin.username = response["data"]["username"]
                })
        }
    },
    created: function() {
        // Get server name
        axios.get("/server_name")
            .then(function(response) {
                vue_admin.server_name = response["data"]["server_name"]
            })
        this.is_admin()
        this.get_username()
        this.list_users()
    }
})