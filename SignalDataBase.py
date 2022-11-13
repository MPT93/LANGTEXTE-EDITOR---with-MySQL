import mysql.connector
from credentials import Credentials
import csv
import os
import glob


class SignalDataBase ():
    def __init__(self, database_name="signals"):

        self.database_name = database_name

    def connect_with_database(self):
        try:
            self.connection = mysql.connector.connect(
                user=Credentials.USER.value, password=Credentials.PASSWORD.value, host=Credentials.HOST.value)
            self.cursor = self.connection.cursor()

            return True

        except mysql.connector.errors.ProgrammingError:

            return False

    def try_to_select_existing_database(self):
        try:
            query = 'USE {}'.format(self.database_name)
            self.cursor.execute(query)

            return True

        except mysql.connector.errors.ProgrammingError:

            return False

    def create_empty_database(self):

        self.drop_database()

        query = 'CREATE DATABASE IF NOT EXISTS {}'.format(
            self.database_name)
        self.cursor.execute(query)

        query = 'USE {}'.format(self.database_name)
        self.cursor.execute(query)

    def get_amount_of_csv_files_good_to_create_database(self, base_path):

        recursive_path = os.path.join(base_path, "**/*.csv").replace("\\", "/")
        amount_of_csv_files = len(glob.glob(recursive_path, recursive=True))

        return amount_of_csv_files

    def create_and_fill_table(self, path, table_name):

        try:
            if table_name != "Leer":

                query = 'CREATE TABLE IF NOT EXISTS {} (signals VARCHAR(255), descriptions VARCHAR(255))'.format(
                    table_name)
                self.cursor.execute(query)

                with open(path, "r") as file:
                    fileReader = csv.reader(file, delimiter=";")
                    for line in fileReader:
                        query = 'INSERT INTO {} (signals, descriptions) VALUES ( %s, %s)'.format(
                            table_name)

                        self.cursor.execute(query, (line[0], line[1]))
                        self.connection.commit()

            return True

        except IndexError:
            self.drop_database()

            return False

        except mysql.connector.errors.ProgrammingError:
            self.drop_database()

            return False

    def select_application(self, table_name):

        query = 'SELECT * FROM {}'.format(table_name)
        self.cursor.execute(query)

        return self.cursor.fetchall()

    def get_tables_names(self):

        query = 'SHOW TABLES'
        self.cursor.execute(query)
        tables = self.cursor.fetchall()
        tables_names = []

        for table in tables:
            tables_names.append(table[0])

        return (tables_names)

    def drop_database(self):

        query = 'DROP DATABASE IF EXISTS {}'.format(
            self.database_name)
        self.cursor.execute(query)

    def close_connection(self):

        self.cursor.close()
        self.connection.close()
