import ticketevolution

client_token = 'befb2a67a08949960608a14b3d838485'
client_secret = 'KOpo73I4Cl0QUY7qssY1/nj1TVnz5GEwGoro2iVz'
#client_token = 'abc'
#client_secret = 'xyz'

# GET request
api = ticketevolution.Api(
    client_token = client_token,
    client_secret = client_secret,
    sandbox = True,
    debug=True,
)
#print api._FetchUrl('https://api.sandbox.ticketevolution.com/categories',parameters = {
#    'per_page':1
#})

#print api.GetCategories(per_page=1,name = "a")
#print api.GetCategory(category_id=1)
#print api.GetAddresses(client_id=1,name = "derek")

"""
print api.CreatePhoneNumbers(client_id = 1,numbers = [{
    "number":"301-51-4238",
    "extension":"176"
}])
print api.CreatePhoneNumbers(client_id = 1,numbers = [{
    "number":"301-51-4238",
    "extension":"176"
}])
print api.UpdatePhoneNumber(client_id = 1, phone_number_id=3,phone_number = {
    "extension":"924"    
})
"""
#api._FetchUrl('https://api.sandbox.ticketevolution.com/clients',post_data = {
#    'thisissomedata':"aaarg"
# },http_method = 'POST')

# print api.post("/clients",{
#     "clients":[{
#         "name":"Mister Rogers"
#     }]
# })
# print api.put('/clients/2094',{
#     "name":"Ms Rogers"
# })
# print api.get('/clients/2094')

print api.get('/categories',{
    'per_page':"2",
    'page_num':"1",
})