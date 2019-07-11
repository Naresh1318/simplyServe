let vue_admin = new Vue({
    el: "#app",
    data: {
        add_username: "",
        add_email: "",
        add_password: "",
        delete_email: "",
        log: ""
    },
    methods: {
        add_user: function () {
            axios.post("add_user",
                {
                    "username": vue_admin.add_username,
                    "email": vue_admin.add_email,
                    "password": vue_admin.add_password
                })
                .then(function (response) {
                    if (response["data"]["user_added"]) {
                        vue_admin.add_username = ""
                        vue_admin.add_email = ""
                        vue_admin.add_password = ""
                        vue_admin.log = "User added!"
                    }
                    else {
                        vue_admin.log = "Email taken :("
                    }
                })
        },
        delete_user: function () {
            axios.post("delete_user",
                {
                    "email": vue_admin.delete_email
                })
                .then(function (response) {
                    if (response["data"]["user_deleted"]) {
                        vue_admin.delete_email = ""
                        vue_admin.log = "User deleted"
                    }
                    else {
                        vue_admin.log = "User not found :("
                    }
                })
        }
    }
})