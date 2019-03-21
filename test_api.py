"""
Testing our API.
"""

import sys
import random
import string

import csv
import unittest

import requests


URL = 'http://localhost:8078/get_config'
SUCCESS_CODE = 200
BAD_REQUEST_CODE = 400
RAINY_DAY_REQUESTS_NUMBER = 3

CSV_DEVELOPE_FILENAME = 'sunny_days_develop_mr_robot_configs.csv'
CSV_VPN_FILENAME = 'sunny_days_test_vpn_configs.csv'

REQUEST_DEVELOP_EXAMPLE = {'Type': 'Develop.mr_robot', 'Data': 'YHySKtEhYm'}
RESPONSE_DEVELOP_EXAMPLE = {
    'Data': 'YHySKtEhYm',
    'Host': 'WKyh',
    'Port': 46836,
    'Database': 'vkNMTN',
    'User': 'zmPBh',
    'Password': 'teBuZLhZ',
    'Schema': 'YUEZgVvd'
}

REQUEST_TEST_VPN_EXAMPLE = {
    'Type': 'Test.vpn',
    'Data': 'cHAIJmCYyn'
}

RESPONSE_TEST_VPN_EXAMPLE = {
    "Data": "cHAIJmCYyn",
    "Host": "fhhp",
    "Port": 12210,
    "Virtualhost": "HkJaQ",
    "User": "fPMUz",
    "Password": "RYEeVKFn"
}

TEST_REQUESTS_AND_RESPONSES_LIST = [
    (
        REQUEST_DEVELOP_EXAMPLE,
        RESPONSE_DEVELOP_EXAMPLE
    ),
    (
        REQUEST_TEST_VPN_EXAMPLE,
        RESPONSE_TEST_VPN_EXAMPLE
    )
]

RESPONSE_BAD_INPUT = {'error': 'Bad input'}
RESPONSE_NO_MODEL = {'error': 'config model not present'}
RESPONSE_NOT_FOUND = {'error': 'record not found'}

TEST_UNEXPECTED_BEHAVIOURS_LIST = [
    (
        REQUEST_DEVELOP_EXAMPLE,
        SUCCESS_CODE,
        RESPONSE_DEVELOP_EXAMPLE
    ),
    (
        None,
        BAD_REQUEST_CODE,
        RESPONSE_BAD_INPUT
    ),
    (
        '',
        BAD_REQUEST_CODE,
        RESPONSE_BAD_INPUT
    ),
    (
        {'Type1': '', 'Data': ''},
        BAD_REQUEST_CODE,
        RESPONSE_NO_MODEL
    ),
    (
        {'Type': '', 'Data1': ''},
        BAD_REQUEST_CODE,
        RESPONSE_NO_MODEL
    ),
    (
        {'Type': '', 'Data': ''},
        BAD_REQUEST_CODE,
        RESPONSE_NO_MODEL
    ),
    (
        {'Type': '', 'Data': 'YHySKtEhYm'},
        BAD_REQUEST_CODE,
        RESPONSE_NO_MODEL
    ),
    (
        {'Type': 'Develop.mr_robot', 'Data': ''},
        BAD_REQUEST_CODE,
        RESPONSE_NOT_FOUND
    ),
    (
        {'Type': 'Develop.mr_robota', 'Data': 'YHySKtEhYm'},
        BAD_REQUEST_CODE,
        RESPONSE_NO_MODEL
    ),
    (
        {'Type': 'Develop.mr_robot', 'Data': 'YHySKtEhYma'},
        BAD_REQUEST_CODE,
        RESPONSE_NOT_FOUND
    ),
    (
        {'Type': 123, 'Data': 'YHySKtEhYm'},
        BAD_REQUEST_CODE,
        RESPONSE_BAD_INPUT
    ),
    (
        {'Type': 'Develop.mr_robot', 'Data': 123},
        BAD_REQUEST_CODE,
        RESPONSE_BAD_INPUT
    )
]


def make_request(json_request, url=URL):
    """Send json request, return response object."""
    return requests.post(url=url, json=json_request)


class BaseCompareTesting(unittest.TestCase):
    """Parent test case for check compliance in request and response."""

    def _test_comparing_response_data(self, test_req_resp_data):
        """Comparing with test responses."""
        for test_req, test_resp in test_req_resp_data:
            with self.subTest(test_request=test_req, test_response=test_resp):
                print('request:  ', test_req)
                resp = make_request(json_request=test_req)
                print('response: ', resp.json())
                self.assertEqual(resp.json(), test_resp)


class TestTechnicalTask(BaseCompareTesting):
    """Main test case for check compliance with the technical task."""

    def test_response_status_code(self):
        """Checking response status."""
        resp = make_request(json_request=REQUEST_DEVELOP_EXAMPLE)
        self.assertEqual(resp.status_code, SUCCESS_CODE)

    def test_comparing_response_data(self):
        """Comparing with technical test responses."""
        print('\nCompare response with test response for technical requests')
        self._test_comparing_response_data(
            test_req_resp_data=TEST_REQUESTS_AND_RESPONSES_LIST)


class TestSunnyDays(BaseCompareTesting):
    """Test case for sunny day scenarios."""

    @staticmethod
    def _load_csv(csv_filename):
        csv_list = []
        with open(csv_filename, newline='') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter='|')
            for row in csvreader:
                # skip whitespaces using strip
                stripped_row = {elem.strip():row[elem].strip() for elem in row}
                csv_list.append(stripped_row)
        return csv_list

    @classmethod
    def _generate_test_list(cls, csv_filename):
        """
        Generate test list from csv raw data in that format:
        [ (request_0, response_0), (request_1, response_1), ... ]
        """
        csv_data_list = cls._load_csv(csv_filename)
        if csv_filename == CSV_VPN_FILENAME:
            type_string = 'Test.vpn'
        else:
            type_string = 'Develop.mr_robot'
        req_resp_data_list = []

        for row in csv_data_list:
            test_req = {
                'Type': type_string,
                'Data': row['data']
                }
            # make every first letter upper
            test_resp = {elem[0].upper()+elem[1:] : row[elem] for elem in row}
            # save port as int
            test_resp['Port'] = int(test_resp['Port'])
            req_resp_data_list.append((test_req, test_resp))
        return req_resp_data_list

    def setUp(self):
        self.test_develop_mr_robot_configs_data = TestSunnyDays._generate_test_list(
            CSV_DEVELOPE_FILENAME)
        self.test_vpn_configs = TestSunnyDays._generate_test_list(CSV_VPN_FILENAME)

    def test_response_data(self):
        """Comparing responses with sunny day's scenarios requests."""
        print('\nCompare response with test response for sunny days requests')
        for test_data in (self.test_develop_mr_robot_configs_data, self.test_vpn_configs):
            with self.subTest(test_data=test_data):
                print('\nCompare response with test response',
                      'for next sunny days requests:')
                self._test_comparing_response_data(test_req_resp_data=test_data)


class TestRainyDays(BaseCompareTesting):
    """Test case for rainy day scenarios."""

    def setUp(self):
        random_test_requests = []
        for _ in range(RAINY_DAY_REQUESTS_NUMBER):
            for type_string in 'Develop.mr_robot', 'Test.vpn':
                # k=10 - len of generated string
                random_str = ''.join(random.choices(string.ascii_uppercase +
                                                    string.digits, k=10))
                random_dict = {
                    'Type': type_string,
                    'Data': random_str
                    }
                random_test_requests.append(random_dict)
        self.random_test_requests = random_test_requests

    def test_response_data(self):
        """Comparing responses with rainy day's scenarios requests."""
        print('\nCompare response with test response for rainy days requests')
        answer = {'error': 'record not found'}
        for test_req in self.random_test_requests:
            with self.subTest(test_request=test_req):
                print('request:  ', test_req)
                resp = make_request(json_request=test_req)
                print('response: ', resp.json())
                self.assertEqual(resp.json(), answer)


class TestUnexpectedBehaviour(BaseCompareTesting):
    """Test case for unexpected behaviour."""

    def setUp(self):
        self.unexpected_test_requests = TEST_UNEXPECTED_BEHAVIOURS_LIST
        self.expected_test_response = []

    def test_unexpected_requests(self):
        """Comparing responses with unexpected requests."""
        print('\nComparing responses with unexpected requests.')
        output_string = '{0!s:>57} => {1!s:^11}|{2!s:<}'
        print(output_string.format('request', 'status code', 'response'))
        for request, status_code, exp_response in self.unexpected_test_requests:
            with self.subTest(test_request=request, status_code=status_code,
                              exp_response=exp_response):
                response = make_request(request)
                self.assertEqual(response.status_code, status_code)
                self.assertEqual(response.json(), exp_response)
                print(output_string.format(request, response.status_code,
                                           response.json()))


if __name__ == '__main__':
    unittest.main()
