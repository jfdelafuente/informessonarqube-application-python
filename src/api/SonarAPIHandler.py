import requests
import logging
import os

from dotenv import load_dotenv


class SonarAPIHandler(object):
    """
    Adapter for SonarQube's web service API.
    """
    DEFAULT_BASE_PATH = ''

    # Endpoint for resources and rules
    COMPONENTS_SEARCH_ENDPOINT = '/api/components/search'
    MEASURES_SEARCH_ENDPOINT = '/api/measueres/search'
    MEASURES_SEARCH_HISTORY_ENDPOINT = '/api/measures/search_history'
    MEASURES_COMPONENT_ENDPOINT = '/api/measures/component'
    PROJECT_ANALYSES_ENDPOINT = '/api/project_analyses/search'
    PROJECT_SEARCH_ENDPOINT = '/api/projects/search'
    QUALITYGATE_BYPROJECT_ENDPOINT = '/api/qualitygates/get_by_project'

    METRICS = "alert_status, complexity, duplicated_lines_density, code_smells, sqale_rating, sqale_index,\
        sqale_debt_ratio, bugs, reliability_rating, vulnerabilities, security_rating, ncloc, coverage"
        

    def __init__(self, host=None, base_path=None):
        """
        Set connection info and session, including auth (if user+password
        and/or auth token were provided).
        """
        load_dotenv()
        self._host = host or os.environ['SONAR_DEFAULT_HOST']
        self._base_path = base_path or self.DEFAULT_BASE_PATH
        self.token = os.environ['SONAR_ACCESS_TOKEN']
        # print("Conectando con : %s" % self._host)

    def _get_url(self, endpoint):
        """
        Return the complete url including host and port for a given endpoint.
        :param endpoint: service endpoint as str
        :return: complete url (including host and port) as str
        """
        return '{}{}{}'.format(self._host, self._base_path, endpoint)

    def _make_call(self, endpoint, **query_args):
        """
        Make the call to the service with the given queryset and query_args,
        using the initial session.
        Note: data is not passed as a single dictionary for better testability
        (see https://github.com/kako-nawao/python-sonarqube-api/issues/15).
        :param endpoint: relative url to make the call
        :param query_args: queryset or body
        :return: response
        """
        # Get method and make the call
        url = self._get_url(endpoint)
        # print(url)

        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query_args
        )
        return response

    def get_component(self, qualifiers, index):
        query_args = {
            'qualifiers': qualifiers,
            'p': index,
            'ps': '200'
        }
        logging.debug(query_args)
        datos = self._make_call(self.COMPONENTS_SEARCH_ENDPOINT, **query_args)
        return datos

    def get_project(self, componente_list):
        query_args = {
            'projects': componente_list,
            'qualifiers': "TRK",
            'ps': '200'
        }
        logging.debug(query_args)
        datos = self._make_call(self.PROJECT_SEARCH_ENDPOINT, **query_args)
        return datos

    def get_qualitygate_by_project(self, component):
        query_args = {
            'project': component
        }
        logging.debug(query_args)
        datos = self._make_call(self.QUALITYGATE_BYPROJECT_ENDPOINT, **query_args)
        return datos
    
    def get_measures_component(self, component):
        query_args = {
            'component': component,
            'additionalFields': 'metrics, periods',
            'metricKeys': self.METRICS
        }
        logging.debug(query_args)
        body = self._make_call(self.MEASURES_COMPONENT_ENDPOINT, **query_args)
        return body

    def get_measures_history(self, component):
        query_args = {
            'component': component,
            'metrics': self.METRICS
        }
        logging.debug(query_args)
        body = self._make_call(
            self.MEASURES_SEARCH_HISTORY_ENDPOINT, **query_args)
        return body

    def get_measures_history_from(self, component, fecha):
        query_args = {
            'component': component,
            'metrics': self.METRICS,
            'from': fecha
        }
        logging.debug(query_args)
        body = self._make_call(
            self.MEASURES_SEARCH_HISTORY_ENDPOINT, **query_args)
        # logging.debug(body.text)
        return body

    def get_project_analyses(self, component):
        query_args = {
            'project': component,
            # 'category': 'VERSION',
            'p': 1,
            'ps': 100
        }
        logging.debug(query_args)
        body = self._make_call(self.PROJECT_ANALYSES_ENDPOINT, **query_args)
        return body

    def get_project_analyses_from(self, component, fecha):
        query_args = {
            'project': component,
            'category': 'VERSION',
            'from': fecha,
            'p': 1,
            'ps': 100
        }
        logging.debug(query_args)
        body = self._make_call(self.PROJECT_ANALYSES_ENDPOINT, **query_args)
        return body
