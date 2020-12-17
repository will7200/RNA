from urllib.parse import urlparse, urljoin

from flask import request


def is_safe_url(target):
    """Check if target will lead to the same server
    Ref: https://web.archive.org/web/20190128010142/http://flask.pocoo.org/snippets/62/
    :param target: The redirect target
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
            test_url.scheme in ("http", "https")
            and ref_url.netloc == test_url.netloc
    )
