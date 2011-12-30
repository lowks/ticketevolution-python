'''A library that provides a Python interface to the TicketEvolution API'''

__author__ = 'derekdahmer@gmail.com'
__version__ = '0.0.1'


import urllib
import urllib2

import urlparse
import gzip
import StringIO
import hmac, hashlib, base64
import re
import json

from helpers import get_call

try:
  # Python >= 2.6
  import json
except ImportError:
  try:
    # Python < 2.6
    import simplejson as json
  except ImportError:
    try:
      # Google App Engine
      from django.utils import simplejson as json
    except ImportError:
      raise ImportError, "Unable to load a json library"

class Api(object):
    '''An object containing methods for making requests against
    the ticket evolution exchange API.

    Example usage:

      To create an API object with your credentials:

        >>> import ticketevolution
        >>> api = ticketevolution.Api(client_token = "abc",
                                      client_secret = "xyz")

      To make a GET request:
        
        >>> result = api.get('/categories')
        >>> print [c['name'] for c in result['categories']]

      To make a GET request with parameters:

        >>> result = api.get('/categories', parameters = {
                'per_page':5
                'page_num':1
            })
        >>> print [c['name'] for c in result['categories']]
      
      Making a POST request to create a new client

        >>> result = api.get('/clients', body = {
                "clients": [{
                    "name":"Will Smith"    
                }]
            })
        >>> print [c['id'] for c in result['clients']]

    '''
    def __init__(self,
                 client_token,
                 client_secret,
                 sandbox=False,
                 debug=False,
                 alt_urllib=None):
        '''Instantiate a new ticketevolution.Api object.

        Args:
          client_token:
            Your api auth token.
          client_secret:
            Your api secret key.
          sandbox:
            If set to true, use api.sandbox.ticketevolution.com which
            can be used for testing out queries.  
            Note that this is not a good solution for writing tests, since 
            the sandbox is still subject to rate limits. Instead, in your 
            tests, use a mock Api object that doesn't actually send out 
            requests.  [Optional]
        '''

        self.client_token = client_token
        self.client_secret = client_secret

        self._urllib         = alt_urllib or urllib2
        self._input_encoding = None

        self.API_VERSION = 8

        if sandbox:
            self.BASE_URL = 'https://api.sandbox.ticketevolution.com'
        else:
            self.BASE_URL = 'https://api.ticketevolution.com'

        self.debug = debug

    # # Example of how you could do a more meaningful method.
    # # Putting this off for a later version
    # @get_call('/clients/:client_id/addresses',['name','per_page'])
    # def GetAddresses(self,path, parameters):
    #     return self.get(path, parameters)

    def get(self,path,parameters = {}):
        '''Make a GET request against the API.

        Args:
          path:
            The URL path to access, like /clients/123, not including
            query string parameters.
          parameters:
            A dict whose key/value pairs should encoded and added
            to the query string. [Optional]

        Returns:
          A dict of the JSON response.
        '''
        raw_response = self._FetchUrl(
            path=path, 
            http_method='GET',
            parameters=parameters)
        return json.loads(raw_response)

    def post(self,path,body = {}):
        '''Make a POST request against the API.

        Args:
          path:
            The URL path to access, like /clients/123, not including
            query string parameters.
          body:
            A dict or list to be converted to a JSON string and 
            used in the body of the request. [Optional]

        Returns:
          A dict of the JSON response.
        '''
        post_data = json.dumps(body)
        raw_response = self._FetchUrl(
            path=path, 
            http_method='POST',
            post_data=post_data)
        return json.loads(raw_response)

    def put(self,path,body):
        '''Make a PUT request against the API.

        Args:
          path:
            The URL path to access, like /clients/123, not including
            query string parameters.
          body:
            A dict or list to be converted to a JSON string and 
            used in the body of the request. [Optional]

        Returns:
          A dict of the JSON response.
        '''
        post_data = json.dumps(body)
        raw_response = self._FetchUrl(
            path=path, 
            http_method='PUT',
            post_data=post_data)
        return json.loads(raw_response)


    def _FetchUrl(self,
                  path,
                  http_method = 'GET',
                  post_data=None,
                  parameters={}):
        '''Fetch a URL, optionally caching for a specified time.

        Args:
          path:
            The URL path to access, like /clients/123
          post_data:
            A unicode string to be used as the request body [Optional]
          parameters:
            A dict whose key/value pairs should encoded and added
            to the query string. [Optional]

        Returns:
          A string containing the body of the response.
        '''

        http_handler  = self._urllib.HTTPHandler()
        https_handler = self._urllib.HTTPSHandler()

        opener = self._urllib.OpenerDirector()
        opener.add_handler(http_handler)
        opener.add_handler(https_handler)

        # Create the full URL with QS parameters
        url = self.BASE_URL + path
        url = self._BuildUrl(url, extra_params=parameters)

        self.log("URL: %s" % url)
        self.log("Post Data: %s" % post_data)

        # Sign request
        signature = self._generate_signature(http_method, url, post_data)
        headers = {
            'Accept':"application/vnd.ticketevolution.api+json; version=%s" % self.API_VERSION,
            'X-Signature':signature,
            'X-Token':self.client_token,
        }
        self.log(headers)

        # Open and return the URL immediately if we're not going to cache
        request = self._urllib.Request(url,post_data,headers)
        response = opener.open(request)
        url_data = self._DecompressGzippedResponse(response)
        opener.close()

        # Always return the latest version
        return url_data


    def _generate_signature(self,
                            http_method,
                            url, 
                            encoded_post_data = None):
        '''Creates a signature for the request using 
        either the URL for GET requests or the post data for other
        requests.

        Args:
            http_method:
                GET, POST, PUT, DELETE
            url:
                Full URL we are accessing, including scheme and query string.
            encoded_post_data:
                If not a GET request, include the body data as a string. [Optional]

        '''
        # Remove the 'https://' from the url
        url_without_scheme = url.split("//",1)[1]

        if http_method == 'GET':
            to_sign = url_without_scheme

            # Due to bug in API auth, make sure it has a question mark
            # even if there's no query string params
            if not "?" in url_without_scheme:
                to_sign += "?"
            
            request = "GET %s" % (to_sign)
        else:
            # Use post data after "?" instead of query string
            host_and_path = url_without_scheme.split("?",1)[0]
            request = "%s %s?%s" % (http_method, host_and_path, encoded_post_data)

        signature = hmac.new(
            digestmod=hashlib.sha256,
            key=self.client_secret,
            msg=request,
        ).digest()

        self.log("Signing: " + request)

        encoded_signature = base64.b64encode(signature)
        return encoded_signature


    def _Parse(self, json):
        '''Parse the returned json string
        '''
        try:
            data = simplejson.loads(json)
        except ValueError:
            return data

    def _Encode(self, s):
        if self._input_encoding:
            return unicode(s, self._input_encoding).encode('utf-8')
        else:
            return unicode(s).encode('utf-8')

    def _EncodeParameters(self, parameters):
        '''Return a string in key=value&key=value form

        Values of None are not included in the output string.

        Args:
            parameters:
                A dict of (key, value) tuples, where value is encoded as
                specified by self._encoding

        Returns:
            A URL-encoded string in "key=value&key=value" form
        '''
        if parameters is None:
          return None
        else:
          return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in parameters.items() if v is not None]))

    def _DecompressGzippedResponse(self, response):
        raw_data = response.read()
        if response.headers.get('content-encoding', None) == 'gzip':
            url_data = gzip.GzipFile(fileobj=StringIO.StringIO(raw_data)).read()
        else:
            url_data = raw_data
        return url_data

    def _BuildUrl(self, url, path_elements=None, extra_params=None):
        # Break url into consituent parts
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

        # Add any additional path elements to the path
        if path_elements:
            # Filter out the path elements that have a value of None
            p = [i for i in path_elements if i]
            if not path.endswith('/'):
                path += '/'
                path += '/'.join(p)

        # Add any additional query parameters to the query string
        if extra_params and len(extra_params) > 0:
            extra_query = self._EncodeParameters(extra_params)
            # Add it to the existing query
            if query:
                query += '&' + extra_query
            else:
                query = extra_query

        # Return the rebuilt URL
        return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

    def log(self,message):
        if self.debug:
            print message
