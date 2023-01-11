from typing import (
    Optional,
)

import requests

import frontend.app_constants_new as app_constants_new


_API_URL = f"{app_constants_new.API_HOST}:{app_constants_new.API_PORT}"


def get_data(
        end_point_name: str,
        params: dict=dict(),
        entity_id: Optional[str] = None
    ):
    # Sometimes the end point name starts with /, sometimes it does not.
    # While this is inconsistent
    # it is easier to fix it here, rather than change name of each end point.
    if end_point_name.startswith("/"):
        end_point_name = end_point_name.replace("/", "", 1)
    url_parts = [_API_URL, end_point_name]
    if entity_id is not None:
        url_parts.append(entity_id)
    query = requests.get(
        "/".join(url_parts),
        params=params
    )
    return query.json()


def post_data(end_point_name: str, json_data: dict):
    requests.post(
        f"{_API_URL}/{end_point_name}",
        json=json_data
    )
