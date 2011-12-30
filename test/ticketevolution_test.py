#!/usr/bin/python2.7
'''Unit tests for the ticketevolution library'''

__author__ = 'derekdahmer@gmail.com'

import os
import time
import calendar
import unittest
import urllib
import sys
import collections

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



class ApiTest(unittest.TestCase):
    def setUp(self):
        self.mock_urllib = MockUrllib()
        self.api = ticketevolution.Api(
            client_token = "abcdefghijklmnopqrstuvwxyz123456",
            client_secret = "abcdefghijklmnopqrstuvwxyz12345678901234",
            sandbox = True,
            alt_urllib = self.mock_urllib,
        )

    def testGetCall(self):
        self.mock_urllib.AddFileHandler(
          url = '/categories?per_page=3',
          filename = 'categories.json',
          method = 'GET')

        result = self.api.get('/categories',{
          'per_page':'3'
        })
        self.assertEqual(len(result['categories']),3)


    def testPostCall(self):
        self.mock_urllib.AddFileHandler(
            url = '/clients',
            filename = 'client_post.json',
            method = 'POST')

        result = self.api.post('/clients', body = {
            "name":"Mister Rogers"
        })

        self.assertEqual(len(result["clients"]),1)

    def testPutCall(self):
        self.mock_urllib.AddFileHandler(
            url = '/clients/123',
            filename = 'client_put.json',
            method = 'PUT')

        result = self.api.put('/clients/123', body = {
            "name":"Ms Rogers"
        })

        self.assertEqual(len(result["clients"]),1)

    

  
class MockUrllib(object):
  '''A mock replacement for urllib2 that can return mock response
  objects for requests against urls.'''

  def __init__(self):
      self._handlers = {}

  def AddHandler(self, url, callback, method="GET"):
      '''When urllib calls `url`, then use the string result of calling 
      `callback` as the response data'''
      self._handlers[(url,method)] = callback

  def AddFileHandler(self, url, filename, method="GET"):
      '''When urllib calls `url`, use the contents of `filename` as the
      data in the returned response object.

      Args:
        url: 
          path and query string vars, e.g. /categories?page_num=1
        filename:
          name of file in the 'testdata' directory
      '''
      # Get the full path of the test data file
      directory = os.path.dirname(os.path.abspath(__file__))
      test_data_dir = os.path.join(directory, 'testdata')
      full_path = os.path.join(test_data_dir, filename)

      def response_object_from_file():
          return MockResponse(
              resp_data = open(full_path).read(),
          )

      self.AddHandler(url,response_object_from_file, method)

  def build_opener(self, *handlers):
      return MockOpener(self._handlers)

  def HTTPHandler(self, *args, **kwargs):
      return None

  def HTTPSHandler(self, *args, **kwargs):
      return None
  
  def OpenerDirector(self):
      return self.build_opener()

  def Request(self,url = "",data = None,headers = {}):
      req = MockRequest(url=url,data=data,headers=headers)
      return req


class MockOpener(object):
  '''Simulates a urllib2 opener.  Tests define handlers that return
  mock response objects with predefined body data based on the URL.'''

  def __init__(self, handlers):
    '''
    Arguments:
      handlers:
        A dict of URL paths w/ query strings (/categories?per_page=1) to 
        functions that, when called, will return mock response objects with 
        the appropriate data as the body.
    '''
    self._handlers = handlers
    self._opened = False

  def open(self, request):
    url = request.url
    data = request.data
    method = request.get_method()

    # Only use the path and querystring as the key to the response map
    path_and_querystring = url.split("//",1)[1]
    path_and_querystring = "/" + path_and_querystring.split("/",1)[1]

    if self._opened:
      raise Exception('MockOpener already opened.')

    if (path_and_querystring,method) in self._handlers:
      self._opened = True
      return self._handlers[(path_and_querystring,method)]()
    else:
      raise Exception('Unexpected %s request for URL %s (Checked: %s)' % (method, path_and_querystring, self._handlers))

  def add_handler(self, *args, **kwargs):
      pass

  def close(self):
    if not self._opened:
      raise Exception('MockOpener closed before it was opened.')
    self._opened = False

class MockRequest(object):
    def __init__(self, url, data=None, headers = {}):
        self.url = url
        self.data = data
        self.headers = headers

        # To do PUT and DELETE requests, urllib2 needs you to monkeypatch this method.
        self.get_method = lambda: 'GET'

class MockResponse(object):
    '''Simulates parts of a urllib2 response object
    '''
    def __init__(self, resp_data):
        self.resp_data = resp_data

        # Taking headers directly from a cURL response
        self.headers = {
            'Content-Type': 'application/vnd.ticketevolution.api+json; version=8; charset=utf-8',
            'Transfer-Encoding': 'chunked',
            'Connection': 'keep-alive',
            'Status': '200',
            'X-Powered-By': 'Phusion Passenger (mod_rails/mod_rack) 2.2.10',
            'ETag': '"efc7717e6d42fab9526e3a05f59ceb62"',
            'X-UA-Compatible': 'IE=Edge,chrome=1',
            'X-Runtime': '0.038400',
            'Cache-Control': 'max-age=0, private, must-revalidate',
            'Strict-Transport-Security': 'max-age=31536000',
            'Server': 'nginx/0.7.65 + Phusion Passenger 2.2.10 (mod_rails/mod_rack)',
        }

    def read(self):
        return self.resp_data

if __name__ == '__main__':
    unittest.main()
