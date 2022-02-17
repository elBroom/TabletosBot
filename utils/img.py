import imghdr


def valid_img(file):
    _type = imghdr.what(file)
    return _type in ('gif', 'jpeg', 'png')
