import datetime
import hashlib
import logging
import os

import funcy
import requests


logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] - %(levelname)s - %(message)s')
log = logging.getLogger()


@funcy.retry(3, timeout=lambda a: 2 ** a)
def main():
    """
    @param: dest Destination for downloaded image
    Find the URL of today's image and download it we don't have it.
    Destination filename will be YYYY-mm-dd_{md5dum}.jpg
    """
    dest = './Bing'
    dest_uhd = './Bing-UHD'
    bing_url = 'https://bing.com'
    bing_wp_url = 'https://bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'

    try:
        log.info("Connecting to %s", bing_url)
        response = requests.get(url=bing_wp_url, timeout=5000)
        if not response.ok:
            raise RuntimeError(f"{response.reason}")
    except:
        log.error(f"Could not get data from {bing_url}. Exiting.")
        return

    wp_url_1080 = bing_url + response.json()['images'][0]['url']
    log.info(f"Found 1080P image url in html: {wp_url_1080}")
    wp_url_uhd = wp_url_1080.replace('1920x1080', 'UHD')
    log.info(f"Found UHD image url in html: {wp_url_1080}")
    md5sum_1080 = hashlib.md5(wp_url_1080.encode('utf-8')).hexdigest()
    log.info(f"Hash of 1080P image url: {md5sum_1080}")
    md5sum_uhd = hashlib.md5(wp_url_uhd.encode('utf-8')).hexdigest()
    log.info(f"Hash of UHD image url: {md5sum_uhd}")

    # Build the filename
    image_file_1080 = f"{datetime.date.today().isoformat()}_{md5sum_1080}.jpg"
    image_file_uhd = f"{datetime.date.today().isoformat()}_{md5sum_uhd}.jpg"
    image_fullname_1080 = os.path.join(dest, image_file_1080)
    image_fullname_uhd = os.path.join(dest_uhd, image_file_uhd)

    # Download the file
    try:
        log.info(f"Downloading {wp_url_1080} to {image_fullname_1080}")
        response = requests.get(wp_url_1080, allow_redirects=True)
        if response.ok:
            with open(image_fullname_1080, 'wb') as f:
                log.debug(f"Writing to disk as {image_fullname_1080}")
                f.write(response.content)
        else:
            log.error(f"Could not download {wp_url_1080}, reason: {response.reason}")
    except:
        log.error(f"Could not download {wp_url_1080} to {image_fullname_1080}")
        return

    try:
        log.info(f"Downloading {wp_url_uhd} to {image_fullname_uhd}")
        response = requests.get(wp_url_uhd, allow_redirects=True)
        if response.ok:
            with open(image_fullname_uhd, 'wb') as f:
                log.debug(f"Writing to disk as {image_fullname_uhd}")
                f.write(response.content)
        else:
            log.error(f"Could not download {wp_url_uhd}, reason: {response.reason}")
    except:
        log.error(f"Could not download {wp_url_uhd} to {image_fullname_uhd}")
        return

    # Done
    log.info('Done')


if __name__ == '__main__':
    main()
