class get_call(object):
    '''Decorator for Api methods to easily make GET calls.

    Method keyword arguments are first matched to :tokens in the given
    path, then the remainder of them are given as key:value pairs in the
    `parameters` argument.
    
    Sample definition:
    
      @get_call('/clients/:client_id/addresses',['name','per_page'])
      def GetAddresses(self,path, parameters):
          return self.get(path, parameters)

    Sample usage:

      api.GetAddresses(client_id=1, name='Will')

    This will do a GET call to /clients/1/addresses, with a parameters 
    dict of:
    {
        "name":"Will"
    }
      
    ''' 
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
