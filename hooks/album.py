import glob
import os
import simplejson as json
import requests
import pprint

import Image

pp = pprint.PrettyPrinter(indent=4)

GALLERY_DIR = os.path.abspath('./media/img/gallery/') + '/'
REL_GALLERY_DIR = '/img/gallery/'
FILE_TYPES = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']
THUMB_PREFIX = 'THUMB_'

client_ID = ""  # XXX move to config file
imgur_headers = {'Authorization': 'Client-ID {0}'.format(client_ID)}
ALBUM_URL = "https://api.imgur.com/3/album/{0}/"
ALBUM_CACHE = None

def get_imgur_album(album_id):
    global ALBUM_CACHE
    if not ALBUM_CACHE:
        response = requests.get(
            ALBUM_URL.format(album_id), headers=imgur_headers
        )
        ALBUM_CACHE = json.loads(response.content)
    return ALBUM_CACHE

def get_imgur_album_srcs(page):
    if 'album-id' not in page.meta:
        raise Exception("No album id for {0}".format(page.meta['title']))
    images = get_imgur_album(page.meta['album-id'])['data']['images']
    pp.pprint(images)
    return (
        json.dumps(map(lambda i: i['link'], images)),
        json.dumps(map(lambda i: i['link'].replace('.jpg', 's.jpg'), images))
    )

def scale_imgur_thumb(width, height):
    return 40, 40

def scale_imgur(width, height):
    return 40, 40

def get_imgur_album_xy(page):
    if 'album-id' not in page.meta:
        raise Exception("No album id for {0}".format(page.meta['title']))
    images = get_imgur_album(page.meta['album-id'])['data']['images']
    return (
        json.dumps(
            map(lambda i: scale_imgur_thumb(i['width'], i['height']), images)
        ),
        json.dumps(
            map(lambda i: scale_imgur(i['width'], i['height']), images)
        ),
    )

def get_image_srcs(ctx, page, templ_vars):
    """
    Wok page.template.pre hook
    Get all images in the album as relative paths
    Binds srcs and thumb_srcs to template
    """
    is_imgur = 'source' in page.meta and page.meta['source'] == 'imgur'
    if 'type' in page.meta and page.meta['type'] == 'album':
        album = page.meta
        # get paths of all of the images in the album
        srcs = []
        if is_imgur:
            # bind to template via json
            templ_vars['site']['srcs'], templ_vars['site']['thumb_srcs'] = (
                get_imgur_album_srcs(page)
            )
        else:
            # get absolute paths of images in album for each file type
            for file_type in FILE_TYPES:
                imgs = glob.glob(GALLERY_DIR + album['slug'] + '/*.' + file_type)

                for img in imgs:
                    img_rel_path = (
                        REL_GALLERY_DIR + album['slug'] + '/' + img.split('/')[-1]
                    )
                    srcs.append(img_rel_path)

            # split full srcs and thumb srcs from srcs into two lists
            full_srcs = []
            thumb_srcs = []
            for src in srcs:
                if src.split('/')[-1].startswith(THUMB_PREFIX):
                    thumb_srcs.append(src)
                else:
                    full_srcs.append(src)

            # bind to template via json
            templ_vars['site']['srcs'] = json.dumps(sorted(full_srcs))
            templ_vars['site']['thumb_srcs'] = json.dumps(sorted(thumb_srcs))


def get_image_sizes(ctx, page, templ_vars):
    """
    Wok page.template.pre hook
    Get all images sizes (width/height) since JS doesn't know until loaded
    Binds sizes and thumb_sizes to template
    """
    is_imgur = 'source' in page.meta and page.meta['source'] == 'imgur'
    if 'type' in page.meta and page.meta['type'] == 'album':
        album = page.meta
        # get paths of all of the images in the album
        srcs = []
        if is_imgur:
            # bind to template via json
            sizes = get_imgur_album_xy(page)
            print sizes
            templ_vars['site']['sizes'], templ_vars['site']['thumb_sizes'] = (
                    sizes
            )
        else:
            # get absolute paths of images in album for each file type
            for file_type in FILE_TYPES:
                image_list = (
                    glob.glob(GALLERY_DIR + album['slug'] + '/*.' + file_type)
                )
                srcs += image_list

            # split full srcs and thumb srcs from srcs into two lists
            full_sizes = []
            thumb_sizes = []
            for src in sorted(srcs):
                image = Image.open(src)
                width = image.size[0]
                height = image.size[1]
                size = [width, height]

                if src.split('/')[-1].startswith(THUMB_PREFIX):
                    thumb_sizes.append(size)
                else:
                    full_sizes.append(size)

            # bind to template via json
            templ_vars['site']['sizes'] = json.dumps(full_sizes)
            templ_vars['site']['thumb_sizes'] = json.dumps(thumb_sizes)
