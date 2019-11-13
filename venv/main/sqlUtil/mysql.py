from flaskext.mysql import MySQL
from json import loads
from main.logUtil.logAgent import LogAgent
from enum import Enum

Logger = LogAgent("mysql").get_logger()

resourcesDir = "../resources/"


class CursorByName():
    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        row = self._cursor.__next__()

        return {description[0]: row[col] for col, description in enumerate(self._cursor.description)}


class EasySql:

    prop_type = Enum('props', 'account todo')

    # inintilazied mysql driver
    def __init__(self , flask_app):

        read_db_config=open(resourcesDir + "db-config.json").read()
        config = loads(read_db_config)

        Logger.debug("[  Successfully Load DB Config  ]")

        flask_app.config['MYSQL_DATABASE_HOST'] = config["HOST"]
        flask_app.config['MYSQL_DATABASE_USER'] = config["USER"]
        flask_app.config['MYSQL_DATABASE_PASSWORD'] = config["PASSWD"]
        flask_app.config['MYSQL_DATABASE_DB'] = config["DB"]

        self.mysql = MySQL()
        self.mysql.init_app(flask_app)

        # setup qry prop
        self.qry = EasySql.load_properties()
        self.init_table()

    # init table
    def init_table(self):
        conn = self.mysql.connect()

        props = list(self.prop_type)
        for value in props :
            create_qrys = self.qry[value.name]["CREATE"]

            for k, v in create_qrys.items():
                try:
                    Logger.debug("Create Query : " + k)
                    conn.cursor().execute(v)
                except Exception as e:
                    pass

        conn.commit()
        conn.close()

        Logger.debug("[ Successfully Initialize table ]")

    # excute qry
    def excute_query(self, prop ,crud_type, query_name  , *value):

        # print(self.qry[prop.name][crud][query_name])
        conn = self.mysql.connect()
        ret_result = None

        try:
            with conn.cursor() as cursor:
                sql = self.qry[prop.name][crud_type][query_name]
                cursor.execute(sql , value)
                result = cursor.fetchall()

                des = cursor.description
                ret_result = []
                for ri , res in enumerate(result):
                    tmp_dict = {}
                    for idx , val in enumerate(res):
                        tmp_dict[des[idx][0]] = val
                    ret_result.append(tmp_dict)

        except Exception as e:
            return None, e.__str__()

        finally:
            conn.commit()
            conn.close()

        return ret_result, None



    @staticmethod
    def load_properties():
        # set json path
        account_qry_path = resourcesDir + "account-db-properties.json"
        todo_qry_path = resourcesDir + "todo-db-properties.json"

        # read json by path
        read_account_qry = open(account_qry_path).read()
        read_todo_qry = open(todo_qry_path).read()

        # input data as jsonFormat
        Logger.debug("[  Successfully Load DB Query  ]")
        return { "account" : loads(read_account_qry),
                 "todo"    : loads(read_todo_qry) }


