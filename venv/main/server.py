'''
will be runable code here .. server.py is starting point to TODO-SERVER ..
'''
from flask import Flask , request , jsonify
from main.sqlUtil.mysql import EasySql
from main.auth.defender import Defender
from main.logUtil.logAgent import LogAgent

# generate logger instance
accountLogger = LogAgent("account").get_logger()

# app and auth class genrate instance
app = Flask(__name__)
auth = Defender("HARDMODE")

# mysql service instance init
mysql = EasySql(app)

# user rest callback method.
def user_callback():
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
                stored_passwd = res[0][0]
                stored_passwd_salt = res[0][1]

                hash_passwd = auth.genHash(passwd.encode('utf-8'), stored_passwd_salt.encode('utf-8'))

                if hash_passwd.decode('utf-8') == stored_passwd:
                    accountLogger.debug("result:login succ ")
                    return jsonify({'message': 'succ', 'code': 1})
                else:
                    accountLogger.debug("result:login fail ")
                    return jsonify({'message': 'login fail', 'code': -1})
        else:
            accountLogger.debug("result:"+ err)
            return jsonify({'message': err, 'code': -1})

    # USER MODIFIE OR DELETE
    if request.method == 'POST':
        json_data = request.json

        accountLogger.debug("[  USER MODIFY  ]")

        # session check.. delete 시 정말 유저가 로그인을 한 상태인지를 체크해야한다.

        userid = json_data['userid']
        action = json_data['action']

        res = None
        err = None

        # action code : 0 = modified , 1 = delete
        if action == 0:
            res, err = mysql.excute_query(mysql.prop_type.account, "DELETE", "DELETE_USER", userid)

        elif action == 1:
            # check before and change passwd ..  change passwd , passwdsalt
            res, err = mysql.excute_query(mysql.prop_type.account, "UPDATE", "UPDATE_USER_PASSWORD", "123" , "123" , userid)
        else:
            err = "unable action"

        if err is None:
            accountLogger.debug("result:modify succ")
            return jsonify({'message':'modify succ', 'code': 1})
        else:
            accountLogger.debug("result: modify fail ~ " + err)
            return jsonify({'message': err, 'code': -1})

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

def todo_callback():
    pass


app.add_url_rule('/user', 'user', user_callback , methods = ['GET','POST','PUT','PATCH'])

app.run(host='0.0.0.0')
