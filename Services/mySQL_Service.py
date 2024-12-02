
import mysql.connector
from mysql.connector import Error
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.testing import fails

import threading


from FileMeneger import read_line_from_file
from Models.alarm_model import AlarmModel
from myLogger import write_error_line, write_info_line


class MysqlDal:

    __dropAlarmTable = "DROP TABLE `vms`.`alarms`"
    __createAlarmTable = "CREATE TABLE `vms`.`alarms` (" \
                        "`alarm_id` INT AUTO_INCREMENT ,"\
                        "`date`  DATETIME DEFAULT CURRENT_TIMESTAMP,"\
                        "`severity` int DEFAULT 0,"\
                        "`desc` varchar(255),"\
                        "PRIMARY KEY (`alarm_id`))"
    crate_table = True
    # Create a Lock object
    crate_table_lock = threading.Lock()
    port = 3333
    ip_address = "127.0.0.1"
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def __init__(self, do_test_connection = True):
        # print("MysqlDal")
        #172.17.0.1:48040
        try:
            self.conn_str = self.__set_connection_string()

            if do_test_connection:
                with MysqlDal.crate_table_lock:
                    if MysqlDal.crate_table:
                        MysqlDal.crate_table = False
                        self.__create_alarm_table()

        finally:
            write_info_line("MysqlDal: init done")


    def update_connection_ip(self,ip,port):
        MysqlDal.port = port
        MysqlDal.ip_address = ip
        self.conn_str = self.__set_connection_string()

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @staticmethod
    def __set_connection_string():
        return {
                'user': 'root',
                'password': 'pulse',
                'port': f"{MysqlDal.port}",
                'host': f"{MysqlDal.ip_address}",
                'database': 'vms',
                'raise_on_warnings': True
            }


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def __disconnect_to_db(self):
        try:
            write_info_line(f"Call __disconnect_to_db")
            if self.connection.is_connected():
                self.connection.close()
        except Error as e:
            write_error_line(f"Error: {e}")

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def __connect_to_db(self):
        try:
            write_info_line(f"Call __connect_to_db")
            # Establish a connection to the MySQL database
            self.connection = mysql.connector.connect(**self.conn_str)
            if self.connection.is_connected() is False:
                write_error_line("Connected to the database failed")
        except Error as e:
            write_error_line(f"Error: {e}")

    def __if_table_exists(self,schema_name, table_name):
        try:
            # query = "SELECT COUNT(*) FROM information_schema.TABLES WHERE(TABLE_SCHEMA='%s') AND (TABLE_NAME='%s')"
            query ="SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s"
            self.__connect_to_db()
            cursor = self.connection.cursor()
            cursor.execute(query, (schema_name, table_name,))  # Pass parameters as a tuple
            result = cursor.fetchone()  # Use fetchone() to get a single result (tuple)
            count = result[0] > 0 if result else False
            return count > 0  # Return True if the table exists, False otherwise
        except Exception as e:
            write_error_line(f"__if_table_exists {e}")
        finally:
            self.__disconnect_to_db()

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def __create_alarm_table(self):
        try:
            table_exists = self.__if_table_exists("vms","alarms")
            write_info_line("call __create_alarm_table")
            self.__connect_to_db()
            cursor = self.connection.cursor()
            if table_exists:
                cursor.execute(self.__dropAlarmTable)
                print("Table 'alarms' delete successfully.")
            cursor.execute(self.__createAlarmTable)
            self.connection.commit()  # Commit the transaction to save changes
            write_info_line("Table 'alarms' created successfully.")
            cursor.close()
        except Exception as e:
            write_error_line(e)
        finally:
            self.__disconnect_to_db()

    def get_alarms_count(self):
        try:
            write_info_line(f"Call get_alarms_count")
            self.__connect_to_db()
            cursor = self.connection.cursor()
            cursor.execute("SELECT count(alarm_id) FROM vms.alarms")
            result = cursor.fetchone()
            cursor.close()
            return result[0]
        except Exception as e:
            write_error_line(e)
        finally:
            self.__disconnect_to_db()
            write_info_line(f"Call get_alarms_count done")


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def get_alarms(self):
        try:
            write_info_line(f"Call get_alarms")
            self.__connect_to_db()
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM vms.alarms")
            rows = cursor.fetchall()
            write_info_line(f"Number of alarms found { len(rows)}")
            alarms_res = []
            for row in rows:
                alarm_id, date, severity , desc = row  # Assuming order matches class attributes
                print(alarm_id)
                alarm = AlarmModel(alarm_id, date,severity, desc)
                print(alarm.date)
                alarms_res.append(alarm)
            cursor.close()
            return alarms_res
        except Exception as e:
            write_error_line(e)
        finally:
            self.__disconnect_to_db()
            write_info_line(f"Call get_alarms done")


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def insert_alarm(self,severity, desc):
        # print(f"Call insert_alarm")
        try:
            # Use parameterized query to avoid SQL injection
            insert_query = "INSERT INTO vms.alarms (`severity`,`desc`) VALUES (%s,%s)"
            self.__connect_to_db()
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (severity,desc,))  # Pass parameters as a tuple
            self.connection.commit()  # Commit the transaction to save changes
            write_info_line(f"Insert alarm: '{desc}' done")
        except Exception as e:
            write_error_line(f"Error during insert_alarm: {e}")
        finally:
            self.__disconnect_to_db()
            # print(f"Call insert_alarm done")


    def insert_alarm_model(self, alarm_model):
        # print(f"Call insert_alarm")
        try:
            # Use parameterized query to avoid SQL injection
            insert_query = "INSERT INTO vms.alarms (`date`,`severity`,`desc`) VALUES (%s,%s,%s)"
            self.__connect_to_db()
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (alarm_model.date,alarm_model.severity, alarm_model.desc,))  # Pass parameters as a tuple
            self.connection.commit()  # Commit the transaction to save changes
            write_info_line(f"Insert alarm model: '{alarm_model.desc}' done")
        except Exception as e:
            write_error_line(f"Error during insert_alarm: {e}")
        finally:
            self.__disconnect_to_db()
            # print(f"Call insert_alarm done")

# if __name__ == '__main__':
# rr = MysqlDal()
# res = rr.get_alarms()
# print(res)