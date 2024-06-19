Adds torrents from crops output to transmission, correctly setting download directory based on existing torrent. 
Requires using [my](https://github.com/deafmute1/crops/tree/store-hashes) fork of crops on branch store-hashes.

# Install
Things you need: `git` (kinda), `python3` (probably at least python3.8)

1. Download using git
`git clone -b store-hashes https://github.com/deafmute1/crops` 
2. Setup python environment
`cd ` 
`python3 -m venv env`
`. env/bin/activate` (or whatever activate script in /bin you need)
`pip3 install -r -requirements.txt`
3. Setup .env
`cp example.env .env`
Modify .env as described in example.env to provide transmission settings.

# Usage 
`python3 ./tr-add-crops.py ` 

