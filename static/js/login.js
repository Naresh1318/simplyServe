let vue_login = new Vue({
    el: "#app",
    vuetify: new Vuetify(),
    data: {
        email: "",
        password: "",
        server_name: "",
        show_alert: false
    },
    methods: {
        /**
         * Try logging in
         */
        login: function () {
            axios.post("/login", {
                email: vue_login.email,
                password: vue_login.password
            })
                .then(function (response) {
                    if (!response["data"]["logged_in"]) {
                        vue_login.email = ""
                        vue_login.password = ""
                        vue_login.show_alert = true
                    }
                    else {
                        window.location.href = "/";
                    }
                })
        }
    },
    /**
     * Get and set server name when page loads
     */
    created: function() {
        axios.get("/server_name")
            .then(function (response) {
                vue_login.server_name = response["data"]["server_name"]
            })
    }
})