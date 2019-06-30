let app = new Vue({
    el: "#app",
    data: {
        message: "Test!!!",
        default_dir: "",
        current_dir: "",
        current_dirs: {},
        current_files: {},
        navigation_stack: [],
        disable_back: true
    },
    methods: {
        /**
        * Gets and sets the default home directory
        */
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
        /**
        * Retrives and sets current_dirs and current_files variables 
        * @param {string} path path to retrive and list files/dirs from 
        */
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
        },
        /**
         * Sets current_dir to the previous dir and updates navigation_stack
         */
        navigate_back: function() {
            let previous_dir = app.navigation_stack.pop()
            app.current_dir = previous_dir
            app.list_dir(app.current_dir)
            if (app.navigation_stack.length < 1)
                app.disable_back = true
        },
        /**
         * Sets current_dir to the required dir and updates navigation_stack
         * @param {string} dir directory to navigate to
         */
        navigate_to: function(dir) {
            app.navigation_stack.push(app.current_dir)
            app.current_dir = app.current_dir + "/" + dir
            app.list_dir(app.current_dir)
            if (app.navigation_stack.length > 0)
                app.disable_back = false
        },
        /**
         * Returns link to the required file on the server
         * @param {string} file file path relative to home/default directory
         */
        get_file_link: function(file) {
            return "/static/linked_dir/" + file 
        }
    },
    /**
     * Performs initial setup when the page is loaded
     */
    created: function() {
        this.initial_setup()
    }
})
