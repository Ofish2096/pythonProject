from sqlalchemy import false
from sqlalchemy.sql.functions import random
import random

import routes

import threading
import time
import datetime

from FileMeneger import read_line_from_file, style
from Services.mySQL_Service import MysqlDal
from myLogger import write_info_line, write_error_line

task_is_active = False

#////////////////////////////////////////////////////////////////////////
def simulate_alarms_task(sleep_time):
    global task_is_active
    thread_id = threading.current_thread().ident

    if task_is_active:
        return

    write_info_line(f"[{thread_id}] -Call simulate_alarms_Task - task_is_active = {task_is_active}")
    task_is_active = True
    is_running = True
    line_index = 3
    number_of_cr = 150
    line=""

    while is_running:
        time.sleep(sleep_time)
        write_info_line(f"{style.BLUE} [{thread_id}] - {datetime.datetime.now()}:sleep({sleep_time}) done{style.GREEN}")
        try:
            if len(line) < number_of_cr:
                line = read_line_from_file("LogSource.txt", line_index)
                line_index += 1
            line_to_log =  line[:number_of_cr]
            line =  cut_the_line(line, number_of_cr)
            if len(line_to_log) > 3 :
                severity = random.randint(0,9)
                generate_alarm(severity,line_to_log)
            elif line == "🍕":#at the enf of file it will return pizza :)
                line_index = random.randint(3, 69)
        except Exception as ex:
            write_error_line(f"Error: simulate_alarms_task {ex} ")

        if sleep_time == 0:
            break
    task_is_active = False
#////////////////////////////////////////////////////////////////////////
def cut_the_line(line, number_of_cr):
    return line[number_of_cr:] if len(line) > number_of_cr else line

#////////////////////////////////////////////////////////////////////////
def generate_alarm(severity,line):
    if len(line) > 5:
        write_info_line(f"{datetime.datetime.now()} :{style.RED} print {line} {style.GREEN}")
        mysql_dal = MysqlDal(True)
        mysql_dal.insert_alarm(severity,line)

#////////////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    write_info_line(f"__name__ == '__main__':")
    t1 = threading.Thread(target=simulate_alarms_task, args=(10,))
    t1.start()
    routs = routes.app.run(host='0.0.0.0', port=5000,debug=True)
    #routs = routes.app.run(debug=False)

