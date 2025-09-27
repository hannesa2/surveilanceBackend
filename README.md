# Simply CRUD backend

It's used to store screenshots in github pull requests

## Configure

Use a `parameter.yml`there is sample included

## Running as daemon

https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55

https://git.mxtracks.info/linuxserver/etcUbuntu/-/commit/0470cf3fbeb20015a163937a072974bf249e34f7
```
sudo vi /etc/systemd/system/githubArtifactsPy.service
sudo systemctl daemon-reload
sudo systemctl start githubArtifactsPy.service
```

## Usage

http://127.0.0.1:5001

### POST

`curl -i -F "file=@/Path/to/your/file" http://127.0.0.1:5001/`

### GET

`http://127.0.0.1:5001/uploads/<filenam>`
