import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__) 
mysql = MySQL(server) 

#config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization # this auth object gives us access to email and password from the basic authentication header
    if not auth:
        return "missing credentials", 401
    
    # check db for username and password
    cur = mysql.connection.cursor() # a mysql cursor is a python object interact with the MySQL server using a MySQLConnection object to execute sql operations
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fetchone() # checks if the res is in database then uses the cur object to retrieve it into a tuple
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401


@server.route("/validate", method=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"] # pull encoded jwt from request

    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1] # getting the authorization bearer token

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithm=["HS256"]
        )
    except:
        return "not authorized", 403
    return decoded, 200 

# function to create the JWT 
def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )  

if __name__ == "__main__": # whenever I run my file using the python command, do the following
    server.run(host="0.0.0.0", port=5000) 