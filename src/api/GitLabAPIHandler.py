# Import the required libraries
import requests
import pandas as pd
import os
from dotenv import load_dotenv

class GitLabAPIHandler(object):
    """
    Adapter for JIRA web service API.
    """
    # Default host is local
    # DEFAULT_HOST = 'https://'
    DEFAULT_BASE_PATH = '/api/v4'

    # Endpoint for resources and rules
    GITLAB_PROJECT_SEARCH_ENDPOINT = '/projects'
    GITLAB_COMMITS_SEARCH_ENDPOINT = '/projects/{}/repository/commits/master'
    GITLAB_PIPELINE_SEARCH_ENDPOINT= '/projects/{}/pipelines/{}'


    def __init__(self, host=None, port=None, base_path=None):
        load_dotenv()
        self._host = host or os.environ['GITLAB_DEFAULT_HOST']
        self._base_path = base_path or self.DEFAULT_BASE_PATH
        self.token = os.environ['GITLAB_ACCESS_TOKEN']
        print(
            f"GitLab: Conectando {self._host} ")

    def _get_url(self, endpoint):
        return '{}{}{}'.format(self._host, self._base_path, endpoint)

    def _make_call(self, endpoint, **query_args):
        # Get method and make the call
        url = self._get_url(endpoint)
        print(url)
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # auth = HTTPBasicAuth(self.usuario, self.password)

        
        response = requests.request(
	        "GET",
	        url,
	        headers=headers,
	        params=query_args
        )
        return response
    

    def get_commits(self, issue):
        query_args = {
        }
        print(query_args)
        body = self._make_call(self.GITLAB_COMMITS_SEARCH_ENDPOINT.format(issue),
                               **query_args)
        return body
    
    def get_projects(self):
        query_args = {

        }
        print(query_args)
        body = self._make_call(self.GITLAB_PROJECT_SEARCH_ENDPOINT, **query_args)
        return body
    
    def get_pipeline(self, project, pipeline):
        query_args = {
        }
        body = self._make_call(self.GITLAB_PIPELINE_SEARCH_ENDPOINT.format(project, pipeline),
                               **query_args)
        return body
    
        
    