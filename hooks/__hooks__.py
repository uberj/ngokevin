from hooks import compile_sass

import thumbnail
from gallery import Gallery

gallery = Gallery()

hooks = {
    #'site.start': [thumbnail.create_thumbnails],
    #'site.output.post':[compile_sass],
    #'site.start': [thumbnail.create_thumbnails],
    'page.meta.post': [gallery.get_images],
    'page.template.pre': [gallery.get_albums, gallery.set_images]
}
