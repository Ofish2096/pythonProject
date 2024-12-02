

from flask import jsonify

from myLogger import write_info_line


def convert_alarm_list_to_json(alarm_last):
    alarms_res = []
    try:

        alarm_h = {"AlarmCount": len(alarm_last)}
        alarms_res.append(alarm_h)
        for alarm in alarm_last:
            alarm_dict = {
                "id": alarm.id,
                "date": str(alarm.date),
                "desc": alarm.desc
            }
            write_info_line(alarm.date)  # For debugging, can be removed in production
            alarms_res.append(alarm_dict)
    except Exception as e:
        write_info_line(f"Error occurred while converting alarms: {e}")
        # Return the error in JSON format
        return {"error": "An error occurred while converting alarm list to JSON.", "message": str(e)}, 400

    # Return the list of alarms as a JSON response
    return alarms_res, 200