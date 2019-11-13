'''
will be runable code here .. server.py is starting point to TODO-SERVER ..
'''
from flask import Flask , request , jsonify , wrappers

from functools import wraps
from main.sqlUtil.mysql import EasySql
from main.auth.defender import Defender
from main.logUtil.logAgent import LogAgent
import jwt

# generate logger instance
accountLogger = LogAgent("account").get_logger()
todoLogger = LogAgent("todo").get_logger()

# app and auth class genrate instance
app = Flask(__name__)
auth = Defender()

app.config["JWT_SECRET_KEY"] = "secrete"

# mysql service instance init
mysql = EasySql(app)

def check_access_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, app.config["JWT_SECRET_KEY"], "HS256")
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                accountLogger.debug("[ NO TOKEN ACCESS ]")
                return jsonify({'message': 'no token', 'code': -1})

            userid = payload["userid"]
        else:
            accountLogger.debug("[ NO TOKEN ACCESS ]")
            return jsonify({'message': 'no token', 'code': -1})

        return f(userid , *args, **kwargs)

    return decorated_function

# user rest callback method.
def user_callback():

    @check_access_token
    def auth_check(userid):
        return userid

    # user auth check
    if request.method == 'GET':
        authValue = auth_check()
        if isinstance(authValue, str):
            return jsonify({'message': 'succ', 'userid':authValue , 'code': 1})
        else:
            return jsonify({'message': 'no token', 'code': -1})

    # USER LOGIN
    if request.method == 'PATCH':
        json_data = request.json

        userid = json_data['userid']
        passwd = auth.decrypt(json_data['passwd'])

        accountLogger.debug("[  USER LOGIN  ]")
        accountLogger.debug("userid:"+ userid)

        res , err = mysql.excute_query(mysql.prop_type.account, "SELECT", "QUERY_PASSWORD_BY_USERID" , userid)

        if err is None:
            if not res:
                accountLogger.debug("result:dosen't exsits user ")
                return jsonify({'message': 'dosen\'t exsits user', 'code': -1})

            else:
                stored_passwd = res[0]['passwd']
                stored_passwd_salt = res[0]['passwdsalt']

                hash_passwd = auth.genHash(passwd.encode('utf-8'), stored_passwd_salt.encode('utf-8'))

                if hash_passwd.decode('utf-8') == stored_passwd:

                    payload = {
                        "userid": userid
                    }
                    token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], "HS256")

                    accountLogger.debug("result:login succ")
                    return jsonify({'message': 'succ', 'code': 1 , "access_token" : token.decode("UTF-8")})
                else:
                    accountLogger.debug("result:login fail ")
                    return jsonify({'message': 'login fail', 'code': -1})
        else:
            accountLogger.debug("result:"+ err)
            return jsonify({'message': err, 'code': -1})

    if request.method == 'POST':

        authValue = auth_check()

        if isinstance(authValue, str):
            json_data = request.json

            accountLogger.debug("[  USER MODIFY  ]")
            action = json_data['action']


            if action == 0:
                res, err = mysql.excute_query(mysql.prop_type.account, "DELETE", "DELETE_USER", authValue)
            elif action == 1:

                change_passwd = json_data['change_passwd']
                change_passwd_salt = json_data['change_passwd_salt']

                res, err = mysql.excute_query(mysql.prop_type.account, "UPDATE", "UPDATE_USER_PASSWORD", change_passwd, change_passwd_salt,
                                              authValue)
            else:
                err = "unable action"
                pass

            if err is None:
                if action == 0:
                    accountLogger.debug("result: `"+ authValue +"` delete succ")
                    pass
                elif action == 1:
                    accountLogger.debug("result:modify succ")
                    pass
                return jsonify({'message': 'succ', 'code': 1})
            else:
                accountLogger.debug("result: modify fail ~ " + err)
                return jsonify({'message': err, 'code': -1})

        else:
            return jsonify({'message': 'no token', 'code': -1})

    # USER INSERT
    if request.method == 'PUT':
        json_data = request.json

        userid = json_data['userid']
        passwd = json_data['passwd']
        passwdSalt = json_data['passwdSalt']

        accountLogger.debug("[  USER JOIN  ]")
        accountLogger.debug("userid:"+ userid)

        res, err = mysql.excute_query(mysql.prop_type.account, "INSERT", "INSERT_USER", userid, passwd , passwdSalt)

        if err is None:
            accountLogger.debug("result:join succ")
            return jsonify({'message': 'succ', 'code': 1})
        else:
            accountLogger.debug("result: join fail ~ " + err)
            return jsonify({'message': err, 'code': -1})

@check_access_token
def todo_callback(userid):

    if request.method == 'GET':
        todoLogger.debug("[  TODO QUERY  ]")
        res, err = mysql.excute_query(mysql.prop_type.todo, "SELECT", "QUERY_TODO_BY_USERID", userid)

        if err is None:
            todoLogger.debug("result:todo select succ")
            return jsonify({'message': 'succ', 'code': 1 , 'data' : res})
        else:
            todoLogger.debug("result: todo select fail ~ " + err)
            return jsonify({'message': err, 'code': -1})
    # action .. 0 delete 1 modified
    if request.method == 'POST':
        json_data = request.json
        print(json_data)

        action = json_data['action']

        if action == 0 :
            todo_no = json_data['todo_no']

            res, err = mysql.excute_query(mysql.prop_type.todo, "DELETE", "DELETE_TODO_BY_TODO_NO", todo_no)

            if err is None:
                todoLogger.debug("result:todo delete succ")
                return jsonify({'message': 'succ', 'code': 1 , 'data' : res})
            else:
                todoLogger.debug("result: todo delete fail ~ " + err)
                return jsonify({'message': err, 'code': -1})
        elif action == 1 :
            todo_no = json_data['todo_no']
            subject = json_data['subject']

            res, err = mysql.excute_query(mysql.prop_type.todo, "DELETE", "DELETE_TODO_BY_TODO_NO", todo_no)

            if err is None:
                todoLogger.debug("result:todo delete succ")
                return jsonify({'message': 'succ', 'code': 1 , 'data' : res})
            else:
                todoLogger.debug("result: todo delete fail ~ " + err)
                return jsonify({'message': err, 'code': -1})

    if request.method == 'PUT':
        json_data = request.json

        todoLogger.debug("[  TODO INSERT  ]")
        # have a access_token
        # subject must be ASE..
        subject = json_data['subject']

        res, err = mysql.excute_query(mysql.prop_type.todo, "INSERT", "INSERT_NEW_TODO", userid , subject)

        if err is None:
            todoLogger.debug("result:todo insert succ")
            return jsonify({'message': 'succ', 'code': 1})
        else:
            todoLogger.debug("result: todo insert fail ~ " + err)
            return jsonify({'message': err, 'code': -1})

    if request.method == 'PATCH':
        return jsonify({'message': 'todo succ', 'code': 1})

app.add_url_rule('/user', 'user', user_callback , methods = ['GET','POST','PUT','PATCH'])
app.add_url_rule('/todo', 'todo', todo_callback , methods = ['GET','POST','PUT','PATCH'])

app.run(host='0.0.0.0')
