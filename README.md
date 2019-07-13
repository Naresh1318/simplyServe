# simplyServe

<p align=center>

<img src="https://raw.githubusercontent.com/Naresh1318/simplyServe/master/static/img/icon.png?token=ADHNPQPRG4VR55RPZ7REC3K5GI5YE" alt="simplyServe" width=20%/>

<p align="center"> Serve directories along with documentations </p>

</p>

# The heck is this?

<p align=center>
    gif
</p>

# Use??

1. Modify paths in `Dockerfile`

2. Run
```bash
docker run -v /home/naresh/Downloads:/simplyServe/static/linked_dir:ro \
           -v /home/naresh/simplyServe/database/:/simplyServe/database/ \
           -p 4000:5000 \
           naresh1318/simply_serve
```

3. Database saved in `/home/naresh/simplyServe/database/`

# Contribute???


Install
1. sudo apt-get install pigz