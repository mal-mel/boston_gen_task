import time
import mysql.connector
import os
import json


class Configurator:
    def __init__(self, config_file: str):
        with open(config_file) as f:
            self.default_config = json.load(f)
        self.config = {}

    @staticmethod
    def nested_get(input_dict, nested_key):
        internal_dict_value = input_dict
        for k in nested_key:
            internal_dict_value = internal_dict_value.get(k, "no_match_option")
            if internal_dict_value == "no_match_option":
                return "no_match_option"
        return internal_dict_value

    def config_get_param(self, *params):
        data = self.nested_get(self.config, params)
        if data == "no_match_option":
            data = self.nested_get(self.default_config, params)
        return data


class DBInterface:
    def __init__(self):
        self.cnx = None
        self.config_obj = Configurator(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json'))
        self._connect()

    def _connect(self):
        time.sleep(1)
        while True:
            print("Try connect")
            try:
                self.cnx = mysql.connector.connect(**self.config_obj.config_get_param("database"))
                self.cnx.autocommit = True
            except mysql.connector.Error as e:
                print(e)
                time.sleep(3)
            else:
                print("Connected to DataBase.")
                break

    def execute(self, query, data):
        result = None
        for i in range(10):
            try:
                cursor = self.cnx.cursor(buffered=True)
                print("Try " + query % data)
                cursor.execute(query, data)
                if 'SELECT' in query:
                    result = cursor.fetchall()
                cursor.close()
            except mysql.connector.Error as e:
                print(e)
                self._connect()
            else:
                return result

    def executemany(self, query, data):
        result = None
        for i in range(10):
            try:
                cursor = self.cnx.cursor(buffered=True)
                print("Try " + query % data)
                cursor.executemany(query, data)
                if 'SELECT' in query:
                    result = cursor.fetchall()
                cursor.close()
            except mysql.connector.Error as e:
                print(e)
                self._connect()
            else:
                return result
