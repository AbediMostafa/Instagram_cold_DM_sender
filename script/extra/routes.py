import requests
from script.models.Setting import Setting

base_url = f"http://{Setting.get_value('server_url')}/"

routes = {
    'get-template': {
        'url': f'{base_url}template/get-template',
        'method': 'POST',
    },

    'delete_template': {
        'url': f'{base_url}template/delete',
        'method': 'POST',
    },
    'process-verify': {
        'url': f'{base_url}process/verify',
        'method': 'POST',
    },

    'check-processes': {
        'url': f'{base_url}processes/check',
        'method': 'POST',
    },

    'get-initial-data': {
        'url': f'{base_url}processes/get-initial-data',
        'method': 'POST',
    },
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
        import traceback

        print(f'Error: {e}')
        # print(traceback.format_exc())

        return None


# --------------------------------------------------
# Templates Routes
# --------------------------------------------------

def get_template(account_id, type):
    return request_to_laravel('get-template', {'id': account_id, 'type': type})


def delete_template(template_ids):
    return request_to_laravel('delete_template', {'ids': template_ids})


# --------------------------------------------------
# Process Routes
# --------------------------------------------------
def process_verify(pid):
    return request_to_laravel('process-verify', {'pid': pid})


def check_processes():
    return request_to_laravel('check-processes')


def get_initial_data():
    return request_to_laravel('get-initial-data')
