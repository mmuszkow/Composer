#!/usr/bin/env python3

import hashlib
import uuid
import cgi
import os, os.path
import urllib, urllib.parse, urllib.request
import mimetypes
from bs4 import BeautifulSoup
import ssl

# format (dir, [url1, url2...])
download = [
    ('samples/gb', ['https://www.vgmusic.com/music/console/nintendo/gameboy/', 'https://www.ninsheetmusic.org/browse/console/GB/', 'https://www.ninsheetmusic.org/browse/console/GBC']),
    ('samples/nes', ['https://www.ninsheetmusic.org/browse/console/NES/', 'https://www.vgmusic.com/music/console/nintendo/nes/'])]

# URL does not always store the filename
def get_filename(url):
    if url.lower().endswith('.mid') or url.lower().endswith('.midi'):
        return os.path.basename(urllib.parse.urlparse(url).path)
    response = urllib.request.urlopen(url)
    try:
        _, params = cgi.parse_header(response.headers.get('Content-Disposition', ''))
        return params['filename']
    except Exception as e:
        ct = response.info()['Content-Type']
        return 'unk_' + str(uuid.uuid4().hex) + mimetypes.guess_extension(ct)

if __name__ == '__main__':
    for download_dir, urls in download:
        for url in urls:
            soup = BeautifulSoup(urllib.request.urlopen(url).read(), 'html.parser')
            for a in soup.find_all('a'):
                href = a.get('href')
                if href and (href.lower().endswith('.mid') or '/mid/' in href):
                    # full URL
                    if not href.startswith('http') and not href.startswith('www.'):
                        href = url + '/' + href

                    path = ''
                    try:
                        path = download_dir + '/' + get_filename(href)
                        if os.path.isfile(path):
                            path += '2.mid' # to avoid overwriting
                        urllib.request.urlretrieve(href, path)
                        print('Downloaded', path)
                    except Exception as e:
                        print('Download failed', path, e)

        # remove duplicates
        hashes = {}
        duplicates = []
        for mid in os.listdir(download_dir):
            fn = download_dir + '/' + mid
            with open(fn, 'rb') as f:
                hasher = hashlib.sha1()
                hasher.update(f.read())
                hash_val = hasher.hexdigest()
                if hash_val in hashes:
                    duplicates.append(fn)
                else:
                    hashes[hash_val] = fn
        for dup in duplicates:
            print('Removing', dup)
            os.unlink(dup)

