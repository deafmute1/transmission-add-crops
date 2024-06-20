#!/usr/bin/env python3
from transmission_rpc import Client
from dotenv import load_dotenv
import bencoder

import os,sys,json,time,argparse
from pathlib import Path
from hashlib import sha1

# minimum percentage of new torrent that must be verified to be on disk
VERIFY_LEEWAY = int(os.environ.get('tr_verify_leeway', 0.05))
VERIFY_TIMEOUT = int(os.environ.get('tr_verify_timeout', 300))

if __name__ == "__main__":
    load_dotenv()
    
    if (len(sys.argv) < 2 or 
        len(sys.argv) > 4 or 
        sys.argv[1] in ("help", "-h", "--help")
    ): 
        print(  
            "USAGE: python3 tr-add-crops.py [--remove] <path> \n\n"
            "path is to a folder of .torrents and a hash-lookup.json file,\n"
            "   as generated by a crops fork with --lookup option\n"
            "--remove: removes torrents which fail to verify against existing files, \n"
            "   instead of leaving them paused"
        )
        exit(0)
    elif sys.argv[1].casefold() == "--remove".casefold():
        remove=True
        path=Path(sys.argv[2]).resolve()
    else: 
        remove=False
        path=Path(sys.argv[1]).resolve()
    
    with path.joinpath('hash-lookup.json').open() as f: 
        hashes=json.load(f)
    
    client = Client(
        protocol=os.environ.get('tr_protocol', 'http'), 
        host=os.environ.get('tr_host', 'localhost'), 
        port=int(os.environ.get('tr_port', 9091)),  
        username=os.environ.get('tr_username', None), 
        password=os.environ.get('tr_password', None)
    )
    
    for torrent_file in path.glob('*.torrent'):
        with torrent_file.open("rb") as f:
            decoded = bencoder.decode(f.read())
        tf_hash = sha1(
            bencoder.encode(decoded[b"info"])
        ).hexdigest().upper()
        try: 
            existing_hash = hashes[tf_hash]
        except KeyError:
            print(f"Skipping {torrent_file.name} as no matching hash found in hash-lookup.json")
            continue
        
        # We are relying on being given good hash mappings to match torrents;
        # don't bother comparing torrent file to existing torrent on deeper level 
        # (i.e. pieces, files etc.)
        new_torrent = client.add_torrent(
            torrent=torrent_file, 
            # rpc returns lower case hashes; one would hope 
            # comparisons on server are case insenstive but just in case.
            download_dir=client.get_torrent(existing_hash.lower()).download_dir,
            paused=True,
            labels=["tr-add-crops"]
        )
        client.verify_torrent(new_torrent.id) 
        timeout = time.time() + VERIFY_TIMEOUT
        while (client.get_torrent(new_torrent.id).status in ("check_pending", "checking")):
            if time.time() >= timeout:
                print("Timeout when verifying file; check tr_verify_timeout var in .env")
            time.sleep(0.5)
        
        #refresh data
        new_torrent = client.get_torrent(new_torrent.id)
        missing_perc=(new_torrent.size_when_done - new_torrent.have_valid)/new_torrent.size_when_done 
        
        # allow some leeway in case of not downloading cover.jpg or some minor corruptions
        if missing_perc > VERIFY_LEEWAY:
            print(
                f"Failed to add, verify and resume from disk torrent {torrent_file.name}" 
                f"with hash {tf_hash}"
            )
            if remove:
                client.remove_torrent(new_torrent.id)
                print(f'Removed this torrent from client')
            continue 
        
        print(f'Successfully added {torrent_file.name} against existing files; starting now')
        client.start_torrent(new_torrent.id)