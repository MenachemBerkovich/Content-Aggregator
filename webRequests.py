"""This module handles the API or any web requests,
during software lifetime. 
"""

from typing import Tuple, Dict, Any

import requests
    

def get_response(**request_params: Dict[str, Any]) -> str:
    """Gets a response from any web source by requests library.
       for a given method (get, post, etc.), url and other variables.
       
    Args:
        Dict[str, Any]: Dictionary, contains request parameters.
        Dictionary should contain some or all of the following parameters:
        {   method: 'get' / 'post',
            url: 'http://example.com/',
            headers: { 'Content-Type': 'application/example' },
            files: None,
            data: None,
            params: None,
            auth: None,
            cookies: None,
            hooks: None,
            json: None
        }

    Returns:
        str: The text of the response.

    Helper functions:
        send_request: Sends the prepared request
        and raise an exception if something fails.
    """
    try:
        with requests.Session() as session:
            request = requests.Request(**request_params)
            response = session.send(session.prepare_request(request), timeout=5)
            if not response.ok:
                print(f"status code is:{response.status_code}")
    except requests.exceptions.RequestException as exc:
        raise exc
    return response.text
