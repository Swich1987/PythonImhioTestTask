"""
Highload API test using locust
"""
from locust import HttpLocust, TaskSet, task
from test_api import URL

REQUEST_DEVELOP_TYPE = {
    'Type': 'Develop.mr_robot',
    'Data': 'YHySKtEhYm'
    }

REQUEST_TEST_VPN_TYPE = {
    'Type': 'Test.vpn',
    'Data': 'cHAIJmCYyn'
    }

PROBABILITY_WEIGHT = 1


class UserBehavior(TaskSet):
    """Describes how user request the API"""

    @task(PROBABILITY_WEIGHT)
    def make_develop_type_request(self):
        """Test requesting Develop.mr_robot"""
        self.client.post(URL, json=REQUEST_DEVELOP_TYPE)

    @task(PROBABILITY_WEIGHT)
    def make_test_vpn_request(self):
        """Test requesting test.vpn"""
        self.client.post(URL, json=REQUEST_TEST_VPN_TYPE)


class WebsiteUser(HttpLocust):
    """Describe user"""
    task_set = UserBehavior
    min_wait_time = 5000 # milliseconds
    max_wait_time = 9000 # milliseconds
