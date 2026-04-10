from __future__ import annotations

import ipaddress
import urllib.parse
import urllib.request

def _should_bypass_proxy(base_url: str) -> bool:
    hostname = urllib.parse.urlparse(base_url).hostname
    if not hostname:
        return False
    if hostname == 'localhost':
        return True
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return hostname.endswith('.local')
    return address.is_private or address.is_loopback or address.is_link_local


def _build_http_opener(base_url: str) -> urllib.request.OpenerDirector:
    if _should_bypass_proxy(base_url):
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener()
