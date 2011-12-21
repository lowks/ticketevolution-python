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

class get_call(object):
    def __init__(self,path,param_names = []):
        self.path = path
        self.path_param_names = re.findall(":([a-zA-Z_]+)",path)
        self.param_names = param_names

    def __call__(self,func):
        def new_func(*args,**kwargs):
            parameters = {}
            path = self.path
            for param_name in self.path_param_names:
                # Replace :tokens in the endpoint with passed in args
                token = ":%s" % param_name
                value = str(kwargs[param_name])
                path = path.replace(token,value)
                del kwargs[param_name]

            for param_name in self.param_names:
                # Create dict of qs params from passed in args
                # that are also allowed param names 
                if param_name in kwargs:
                    parameters[param_name] = kwargs[param_name]
                    del kwargs[param_name]
                
            kwargs['parameters'] = parameters
            kwargs['path'] = path
            return func(*args, **kwargs)
        return new_func


class Api(object):  
    def __init__(self,
                 client_token=None,
                 client_secret=None,
                 sandbox=False):

        self.client_token = client_token
        self.client_secret = client_secret

        self._urllib         = urllib2
        self._input_encoding = None

        self.API_VERSION = 8

        if sandbox:
            self.BASE_URL = 'https://api.sandbox.ticketevolution.com'
        else:
            self.BASE_URL = 'https://api.ticketevolution.com'

    @get_call('/categories',['name','parent_id','per_page','page_num'])
    def GetCategories(self,path, parameters):
        return self.get(path, parameters)
    
    @get_call('/categories/:category_id')
    def GetCategory(self,path,parameters):
        return self.get(path,parameters)

    @get_call('/clients/:client_id/addresses',['name'])
    def GetAddresses(self,path, parameters):
        return self.get(path, parameters)

    def get(self,path,parameters):
        raw_response = self._FetchUrl(
            path=path, 
            http_method='GET',
            parameters=parameters)
        return json.loads(raw_response)

    def post(self,path,body):
        post_data = json.dumps(body)
        raw_response = self._FetchUrl(
            path=path, 
            http_method='POST',
            post_data=post_data)
        return json.loads(raw_response)

    def put(self,path,body):
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

        print "URL: %s" % url
        print "Post Data: %s" % post_data

        # Sign request
        signature = self._generate_signature(http_method, url, post_data)
        headers = {
            'Accept':"application/vnd.ticketevolution.api+json; version=%s" % self.API_VERSION,
            'X-Signature':signature,
            'X-Token':self.client_token,
        }
        print headers

        # Open and return the URL immediately if we're not going to cache
        request = self._urllib.Request(url,post_data,headers)
        response = opener.open(request)
        url_data = self._DecompressGzippedResponse(response)
        opener.close()

        # Always return the latest version
        return url_data


    def _generate_signature(self,
                            http_method,
                            url = None, 
                            encoded_post_data = None):
        '''Creates a signature for the request using 
        either the URL for GET requests or the post data for other
        requests.
        '''

        if http_method == 'GET':
            # Remove the 'https://' from the url
            url_without_scheme = url.split("//",1)[1]

            request = "GET %s" % (url_without_scheme)
        else:
            # Remove the 'https://' and everything after ?
            url_without_scheme = url.split("//",1)[1]
            host_and_path = url_without_scheme.split("?",1)[0]
            request = "%s %s?%s" % (http_method, host_and_path, encoded_post_data)

        signature = hmac.new(
            digestmod=hashlib.sha256,
            key=self.client_secret,
            msg=request,
        ).digest()

        print "Signing: " + request

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
