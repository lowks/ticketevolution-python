#!/usr/bin/python2.7
'''Unit tests for the ticketevolution library'''

__author__ = 'derekdahmer@gmail.com'

import os
import time
import calendar
import unittest
import urllib
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import ticketevolution


class SigningTest(unittest.TestCase):
    def getApi(self):
        return ticketevolution.Api(
            client_token = "abcdefghijklmnopqrstuvwxyz123456",
            client_secret = "abcdefghijklmnopqrstuvwxyz12345678901234",
            sandbox = True,
        )

    # This won't work until we have the authenticator not automatically 
    # add question marks
    def testSignGetWithNoQuestionMark(self):
        api = self.getApi()

        signature = api._generate_signature(
            http_method = "GET",
            url = "https://api.sandbox.ticketevolution.com/clients")
        self.assertEqual(signature, "CZ26dEtpFKkc21yjFK/FeFZ4Ak+9GLbdSQYKffbccd4=")
    
    def testSignGetWithNoQueryParams(self):
        api = self.getApi()

        signature = api._generate_signature(
            http_method = "GET",
            url = "https://api.sandbox.ticketevolution.com/clients?")
        self.assertEqual(signature, "CZ26dEtpFKkc21yjFK/FeFZ4Ak+9GLbdSQYKffbccd4=")
    
    def testSignGetWithSingleQueryParam(self):
        api = self.getApi()

        signature = api._generate_signature(
            http_method = "GET",
            url = "https://api.sandbox.ticketevolution.com/clients?page_num=1")
        self.assertEqual(signature, "1cJFQkqe41x3AF5LPtDccmCvIcw97WXfkGksk+qUvq0=")

    def testSignGetWithMultipleQueryParams(self):
        api = self.getApi()

        signature = api._generate_signature(
            http_method = "GET",
            url = "https://api.sandbox.ticketevolution.com/clients?per_page=1&page_num=1")
        self.assertEqual(signature, "rcqPKvZzaC98SDOLBTTj8k4qIkmdDwnIMjYIKFw+aVY=")


    def testSignPost(self):
        api = self.getApi()

        signature = api._generate_signature(
            http_method = "POST",
            url = "https://api.sandbox.ticketevolution.com/clients",
            encoded_post_data = '{"clients": [{"name": "Will Smith"}]}')
        self.assertEqual(signature, "rcqPKvZzaC98SDOLBTTj8k4qIkmdDwnIMjYIKFw+aVY=")


if __name__ == '__main__':
    unittest.main()