#TicketEvolution Python Library#

_A python wrapper around the TicketEvolution broker exchange API_

##Installing##

###Using pip (recommended)###

pip install ticketevolution

###From source:###

Download the latest ticketevolution-python library from:

http://github.com/ticketevolution/ticketevolution-python

Install the dependencies:

pip install -r requirements.txt

Untar the source distribution and run:

    $ python setup.py build
    $ python setup.py install

###Testing###

With setuptools installed:

    $ python setup.py test

Without setuptools installed:

    $ python ticketevolution_test.py


##Using##

_Look at the method documentation in `ticketevolution.py` for a more indepth overview._

To create an API object with your credentials:

    import ticketevolution
    api = ticketevolution.Api(client_token = "abc",
                              client_secret = "xyz")

To make a GET request:

    result = api.get('/categories')
    print [c['name'] for c in result['categories']]

To make a GET request with parameters:

    result = api.get('/categories', parameters = {
        'per_page':5
        'page_num':1
    })
    print [c['name'] for c in result['categories']]

Making a POST request to create a new client

    result = api.get('/clients', body = {
        "clients": [{
            "name":"Will Smith"    
        }]
    })

##Authors##

*[Derek Dahmer](http://github.com/ddgromit) <derekdahmer@gmail.com>*

_A significant amount of code and inspiration was taken from the awesome [python-twitter](http://code.google.com/p/python-twitter/) library._

##License##
    
    Licensed under the Apache License, Version 2.0 (the 'License');
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
    http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an 'AS IS' BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

