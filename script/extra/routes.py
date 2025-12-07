import requests

base_url = 'http://127.0.0.1/'

routes = {
    'get-name-username': {
        'url': f'{base_url}template/get-name-username',
        'method': 'POST',
    },

    'delete_template': {
        'url': f'{base_url}template/delete',
        'method': 'POST',
    }
}


def request_to_laravel(route_name, data=None):
    route = routes.get(route_name)
    if not route:
        raise ValueError(f'Route "{route_name}" not found.')

    method = route['method'].lower()
    url = route['url']

    try:
        if method == 'get':
            response = requests.get(url, params=data)
        elif method == 'post':
            response = requests.post(url, json=data)
        else:
            raise ValueError('Unsupported HTTP method.')

        response.raise_for_status()
        return response.json() if response.text else None

    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None


def get_name_username(account_id):
    return request_to_laravel('get-name-username', {'id': account_id})


def delete_template(template_ids):
    return request_to_laravel('delete_template', {'ids': template_ids})
