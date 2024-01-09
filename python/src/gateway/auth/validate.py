''' remember, client accesses internal endpoints by first loging in and getting jwt
and for all subsequent requests, the client would have authorization header containing that
jwt which tells our api gateway that that client has access to the endpoints of our overall app.
This module validates that token in the authorization header '''

import os, requests

def token(request):
    if not "Authorization" in request.headers: # if client has authorization header in request
        return None, ("missing credentials", 401)
    
    token = request.headers["Authorization"] # set token equal to authorization

    if not token:
        return None, ("missing credentials", 401) # token doesn not exist 
    
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')/validate}",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        return response.txt, None 
    else:
        return None, (response.txt, response.status_code)