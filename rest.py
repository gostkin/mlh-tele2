from simple_rest_client.api import API
from simple_rest_client.resource import Resource


class Services(Resource):
    actions = {
        'rest_get_available_services': {'method': 'GET', 'url': 'services/available'},
        'rest_get_info': {'method': 'GET', 'url': 'services/{}'}
    }




class Subscribers(Resource):
    actions = {
        'rest_add_service': {'method': 'PUT', 'url': 'subscribers/{}/services/{}'},
        'rest_remove_service': {'method': 'DELETE', 'url': 'subscribers/{}/services/{}'},
        'rest_get_payments': {'method': 'GET', 'url': 'subscribers/{}/payments'},
        'rest_get_user_info': {'method': 'GET', 'url': 'subscribers/{}'},
        'rest_update_user_info': {'method': 'POST', 'url': 'subscribers/{}'},
        'rest_get_balance_info': {'method': 'GET', 'url': 'subscribers/{}/balance'},
        'rest_get_tariff': {'method': 'GET', 'url': 'subscribers/{}/tariff'},
        'rest_set_tariff': {'method': 'POST', 'url': 'subscribers/{}/tariff'},
        'rest_get_service_list': {'method': 'GET', 'url': 'subscribers/{}/services'},
        'rest_get_charges_list': {'method': 'GET', 'url': 'subscribers/{}/charges'}
    }


class Tariffs(Resource):
    actions = {
        'rest_get_available_tariffs': {'method': 'GET', 'url': 'tariffs/available'},
        'rest_get_info': {'method': 'GET', 'url': 'tariffs/{}'}
    }


def build_tele2_api():
    tele2api = API(
        api_root_url='http://tele2-hackday-2017.herokuapp.com/api/',
        params={},
        headers={},
        timeout=2,
        append_slash=False,
        json_encode_body=True
    )

    tele2api.add_resource(resource_name='services', resource_class=Services)
    tele2api.add_resource(resource_name='subscribers', resource_class=Subscribers)
    tele2api.add_resource(resource_name='tariffs', resource_class=Tariffs)

    return tele2api

if __name__ == '__main__':
    api = build_tele2_api()
    print(api.services.get_info('black-list'))

