from urllib.parse import urlunparse


def get_base_url(hostname: str, port: str) -> str:
    scheme = "https" if port == "443" else "http"

    # Construct URL using urllib.parse
    net_loc = f"{hostname}:{port}"
    return urlunparse((scheme, net_loc, "", "", "", ""))