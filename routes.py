import traceback
from datetime import datetime

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

from FileMeneger import style
from Models.alarm_model import AlarmModel
from Services.alarm_service import convert_alarm_list_to_json
from Services.mySQL_Service import MysqlDal
from myLogger import write_info_line, write_error_line

# Initialize Flask app and Flask-RESTX API
app = Flask(__name__)
api = Api(app, version='1.0', title='My API', description='A simple demonstration of Flask-RESTX with Swagger')

# Define the model for the alarm data in Swagger
alarm_model = api.model('Alarm', {
    'date': fields.String(required=True, description='The date and time of the alarm', example='2024-12-01T15:30:00'),
    'severity': fields.String(required=True, description='Severity of the alarm', example='High'),
    'description': fields.String(required=True, description='Description of the alarm',
                                 example='Network issue detected')
})


# Home route
@app.route('/')
def home():
    return '<h1>Flash REST API</h1>'

@api.route('/alarmsCount')  # Use @api.route() instead of @app.route()
class AlarmsCout(Resource):
    def get(self):
        try:
            my_dal = MysqlDal(True)
            return my_dal.get_alarms_count(), 200
        except Exception as e:
            write_error_line(f"Error occurred: {str(e)}")
            write_error_line("Traceback: ".join(traceback.format_exception(None, e, e.__traceback__)))
            return {"error": "An error occurred while processing your request.", "message": str(e)}, 400


# Alarms route - Get the list of alarms
@api.route('/alarms')  # Use @api.route() instead of @app.route()
class Alarms(Resource):
    def get(self):
        """
        This endpoint returns a list of all alarms.
        ---
        responses:
          200:
            description: A list of alarms
            content:
              application/json:
                schema:
                  type: array
                  items:
                    $ref: '#/components/schemas/Alarm'  # Link to the alarm_model
          400:
            description: Bad Request
        """
        try:
            write_info_line(f"{style.BLUE} get alarms() {style.GREEN}")
            my_dal = MysqlDal(True)
            alarms = my_dal.get_alarms()
            return convert_alarm_list_to_json(alarms)
        except Exception as e:
            write_error_line(f"Error occurred: {str(e)}")
            write_error_line("".join(traceback.format_exception(None, e, e.__traceback__)))
            return {"error": "An error occurred while processing your request.", "message": str(e)}, 400


# Define a model for Insert an alarm into the database
alarm_i_model = api.model('insertalarm', {
    'date': fields.String(required=True, description='Alarm date', example='192.168.1.100'),
    'severity': fields.Integer(required=False, description='Alarm severity', example=0),
    'desc': fields.String(required=True, description='Alarm description', example='test test')
})


# Insert alarm route - Insert an alarm into the database
@api.route('/insertalarm')
class InsertAlarm(Resource):
    @api.expect(alarm_i_model)  # Expect an input matching the alarm_model
    def put(self):
        """
        This endpoint inserts a new alarm into the system.
        ---
        requestBody:
          required: true
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Alarm'
        responses:
          200:
            description: Alarm inserted successfully
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 'Alarm inserted successfully'
                    data:
                      type: object
                      properties:
                        date:
                          type: string
                          example: '2024-12-01T15:30:00'
                        severity:
                          type: string
                          example: 'High'
                        description:
                          type: string
                          example: 'Network issue detected'
          400:
            description: Bad Request
        """
        try:
            # Get the JSON data from the request body
            data = request.get_json()
            date = datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M:%S')
            # Print the received data (for debugging purposes)
            write_info_line(data)
            my_dal = MysqlDal(True)
            my_dal.insert_alarm_model(
                AlarmModel(0, date, data.get('severity'), data.get('description'))
            )
            # Return a success response with a 200 OK status
            return  200

        except Exception as e:
            # Log the exception traceback to understand the error better
            write_error_line(f"Error occurred: {str(e)}")
            write_error_line("".join(traceback.format_exception(None, e, e.__traceback__)))
            # Return an error response with a 400 Bad Request status code
            return {"error": "An error occurred while processing your request.", "message": str(e)}, 400


# Define a model for the update request (IP and Port)
update_ip_port_model = api.model('UpdateIPPort', {
    'ip': fields.String(required=True, description='The IP address to be updated', example='192.168.1.100'),
    'port': fields.Integer(required=True, description='The port to be updated', example=8080)
})


# Define a route for updating IP and Port
@api.route('/updateipport')
class UpdateIPPort(Resource):
    @api.expect(update_ip_port_model)  # Expect the request body to match the update_ip_port_model schema
    def put(self):
        """
        This endpoint updates the IP address and port.
        ---
        requestBody:
          required: true
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UpdateIPPort'
        responses:
          200:
            description: IP and Port updated successfully
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 'IP and Port updated successfully'
                    ip:
                      type: string
                      example: '192.168.1.100'
                    port:
                      type: integer
                      example: 8080
          400:
            description: Bad Request
        """
        try:
            # Get the JSON data from the request body
            data = request.get_json()
            ip = data.get('ip')
            port = data.get('port')

            # Validate IP and port
            if not ip or not port:
                return jsonify({"error": "IP and port are required"}), 400
            my_dal = MysqlDal(False)
            my_dal.update_connection_ip(ip, port)

            # For this example, let's assume the save operation is successful.
            write_info_line(f"Updated IP: {ip}, Port: {port}")  # You could log it or store it in your database

            # Return a success response
            return 200

        except Exception as e:
            # Log the exception traceback
            write_error_line(f"Error occurred: {str(e)}")
            write_error_line("".join(traceback.format_exception(None, e, e.__traceback__)))
            return {"error": "An error occurred while processing your request.", "message": str(e)}, 400


# Initialize Swagger UI
if __name__ == '__main__':
    app.run(debug=True)
