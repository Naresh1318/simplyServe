let vue_login = new Vue({
    el: "#app",
    data: {
        email: "",
        password: "",
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
    }
})