var app = new Vue({
    el: "#app",
    data: {
        message: "Test!!!",
        default_dir: {},
        navigation_stack: [],
        current_dir: "",
        current_dirs: {},
        current_files: {},
        disable_back: true
    },
    methods: {
        initial_setup: function() {
            axios.get("/default_dir")
            .then(function (response) {
                console.log(response)
                app.default_dir = response["data"]["default_dir"]
                app.current_dir = app.default_dir
            })
            .catch(function (error) {
                console.log(error)
            })
            .then(function () {
                app.list_dir(app.current_dir)
            })
        },
        list_dir: function(path) {
            return axios.get("/ls", {
                        params: {
                        "path": path
                        }
                   })
                   .then(function (response) {
                        console.log(response)
                        app.current_dirs = response["data"]["dirs"]
                        app.current_files = response["data"]["files"]
                        return
                   })
                   .catch(function (error) {
                        console.log(error)
                   })
                   .then(function () {
                        // always executed
                   })
        },
        navigate_back: function() {
            let previous_dir = app.navigation_stack.pop()
            app.current_dir = previous_dir
            app.list_dir(app.current_dir)
        },
        navigate_to: function(dir) {
            app.navigation_stack.push(app.current_dir)
            app.current_dir = app.current_dir + "/" + dir
            app.list_dir(app.current_dir)
        }
    },
    created: function() {
        this.initial_setup()
    }
})
