# simplyServe

<p align=center>
    <img src="https://raw.githubusercontent.com/Naresh1318/simplyServe/master/static/img/icon.png?token=ADHNPQPRG4VR55RPZ7REC3K5GI5YE" alt="simplyServe" width=20%/>
    <p align="center"> <b>Serve directories along with docs</b> </p>
</p>

# The heck is this?

<p align=center>
    <img src="https://files.naresh1318.com/public/simplyServe/login.png" alt="Demo"/>
    <p align="center"> <b>Login</b> </p>
</p>


Imagine you've collect a ton of data on large number of experiments. Now, imagine you want to share 
it with others and explain how things are organized. You might just host it on any of the file sharing 
services out there and provide additional document that explain how data is organized.  
OR, you can host it yourself. As you may have guessed, simplyServe lets you host file on a 
server and allow restricted access to it. 

Here are some of its features:

1. User access management
<p align=center>
    <img src="https://files.naresh1318.com/public/simplyServe/admin.png" alt="Demo" width="50%"/>
    <p align="center"> <b>Manage users</b> </p>
</p>
2. Multi-file download
3. Document each directory using beautiful charts from chart.js and have it rendered along side each directory
<p align=center>
    <img src="https://files.naresh1318.com/public/simplyServe/home.png" alt="Demo" width="60%"/>
    <p align="center"> <b>Show docs along side files and directories</b> </p>
</p>
4. Easy to setup docker image 

# Use??

Here's I'll explain how you'd serve `/home/naresh/sleep` directory:

1. Download and install docker:

   - Here's a nice guide if you using ubuntu 18.04: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04

2. Clone this repo to any directory, I have it under `/home/naresh/project`

3. Add admin and change server name if needed:

   * Move to the cloned directory `cd simplyServe`

   * Open any editor and modify `Dockerfile`:

     ```bash
     ENV SERVER_NAME "<name>"
     ENV ADMIN_EMAIL "<email>"
     ENV ADMIN_PASS "<pass>"
     ENV ADMIN_NAME "<name>"
     ```

     Here's what my variables look like:

     ```bash
     ENV SERVER_NAME "simplyServe"
     ENV ADMIN_EMAIL "a@1.com"
     ENV ADMIN_PASS "test"
     ENV ADMIN_NAME "admin"
     ```

     * This names your server `simplyServe` and creates an admin user with the your credentials

4. Build your image:

   ```bash
   docker build -t <name> .
   ```

   Here's how mine looks:

   ```bash
   docker build -t simply_serve:latest .
   ```

5. Run your image:

   ```bash
   docker run -v <dir to serve>:/simplyServe/linked_dir:ro \
              -v <dir to create database in>:/simplyServe/database/ \
              -v <dir to store uploaded files>:/simplyServe/public/ \
              -p <port to forward>:5000 \
              <image name>:<tag>
   ```

   Here's mine:

   ```bash
   docker run -v /home/naresh/sleep:/simplyServe/linked_dir:ro \
              -v /home/naresh/simplyServe/database/:/simplyServe/database/ \
              -v /home/naresh/simplyServe/public/:/simplyServe/public/ \ 
              -p 4000:5000 \
              simply_serve:latest
   ```

   This serves `/home/naresh/sleep`, creates a database of users in `/home/naresh/simplyServe/database/` and port farwards the server output into port 4000 on the host machine.

6. Finally, go to `localhost:4000` on your browser and login as admin
