from simple_rest_client.api import API
from simple_rest_client.resource import Resource


class RESTException(Exception):
    def __init__(self, response):
        self.response = response


class Services(Resource):
    actions = {
        'rest_get_available_services': {'method': 'GET', 'url': 'services/available'},
        'rest_get_info': {'method': 'GET', 'url': 'services/{}'}
    }

    def get_available_services(self):
        return self.rest_get_available_services()

    def get_info(self, slug):
        return self.rest_get_info(slug)


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

    def add_service(self, msisdn, x_api_token, slug):
        return self.rest_add_service(msisdn, slug, headers={'X-API-Token': x_api_token})

    def remove_service(self, msisdn, x_api_token, slug):
        return self.rest_remove_service(msisdn, slug, headers={'X-API-Token': x_api_token})

    def get_payments(self, msisdn, x_api_token, from_time, to_time, count):
        return self.rest_remove_service(msisdn, headers={'X-API-Token': x_api_token,
                                                         'Content-Type': 'application/json'}, body={'from': from_time, 'to': to_time, 'count': count})

    def get_user_info(self, msisdn):
        return self.rest_get_user_info(msisdn)

    def update_user_info(self, msisdn, x_api_token, data):
        return self.rest_update_user_info(msisdn, headers={'X-API-Token': x_api_token,
                                                           'Content-Type': 'application/json'}, body={'data': data})

    def get_balance_info(self, msisdn, x_api_token):
        return self.rest_get_balance_info(msisdn, headers={'X-API-Token': x_api_token})

    def get_tariff(self, msisdn, x_api_token):
        return self.rest_get_tariff(msisdn, headers={'X-API-Token': x_api_token})

    def set_tariff(self, msisdn, x_api_token, slug):
        return self.rest_set_tariff(msisdn, body={"tariffSlug": slug},
                                    headers={'X-API-Token': x_api_token, "Content-Type": "application/json"})

    def get_service_list(self, msisdn, x_api_token):
        return self.rest_get_service_list(msisdn, headers={'X-API-Token': x_api_token})

    def get_charges_list(self, msisdn, x_api_token, from_time, to_time, charge_type):
        return self.rest_get_charges_list(msisdn, headers={'X-API-Token': x_api_token,
                                                           'Content-Type': 'application/json'},
                                          body={'from': from_time, 'to': to_time, 'type': charge_type})

class Tariffs(Resource):
    actions = {
        'rest_get_available_tariffs': {'method': 'GET', 'url': 'tariffs/available'},
        'rest_get_info': {'method': 'GET', 'url': 'tariffs/{}'}
    }

    def get_available_tariffs(self):
        return self.rest_get_available_tariffs()

    def get_info(self, slug):
        return self.rest_get_info(slug)


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

