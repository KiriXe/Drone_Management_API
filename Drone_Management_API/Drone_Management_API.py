from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from marshmallow import Schema, fields, validates, ValidationError
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import registry
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

project_path = os.path.dirname(os.path.abspath(__file__))
nombre_bd = 'sqlite.db'
address = os.path.join(project_path, nombre_bd)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{address}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

#model

class Drone(db.Model):

    '''Model of Drone'''
    
    __tablename__ = 'drone'
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    model = db.Column(db.String(20), nullable=False)
    weight_limit = db.Column(db.Float, nullable=False)
    battery_capacity = db.Column(db.Float, nullable=False)
    state = db.Column(db.String(20), nullable=False)
    drone_medications = db.relationship('DroneMedication', back_populates='drone')

class Medication(db.Model):

    '''Model of Medication'''
    
    __tablename__ = 'medication'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    drone_medications = db.relationship('DroneMedication', back_populates='medication')

class DroneMedication(db.Model):

    '''Model of DroneMedication'''
    
    __tablename__ = 'drone_medication'
    id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    medication = db.relationship('Medication', back_populates='drone_medications')
    drone = db.relationship('Drone', back_populates='drone_medications')

# Registration system configuration
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(os.path.join(project_path, 'register.log'), maxBytes=10000, backupCount=1)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

# Flask application logger configuration
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)


# Method to be executed periodically
def check_battery_levels_and_create_audit_log():

    '''Method that will be executed periodically to register the drone battery'''
    
    audit_log = []
    with app.app_context():
        app.logger.info("Audit Log:")
        
        # Verificar si existen drones en la base de datos
        drones = Drone.query.all()

        if not drones:
            app.logger.info("No drones found in the database.")
        else:
            for drone in drones:
                app.logger.info(f'The Drone {drone.serial_number} has {drone.battery_capacity}% of battery')

# Setting up and starting the task scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_battery_levels_and_create_audit_log, trigger='interval', seconds=300)  # Run every 300 seconds
scheduler.start()

# scheme for validation
class DroneSchema(Schema):

    '''Define the drone scheme for validation'''
    
    serial_number = fields.Str(required=True, metadata={'max_length': 100})
    model = fields.Str(required=True, validate=lambda s: s in ["Lightweight", "Middleweight", "Cruiserweight", "Heavyweight"])
    weight_limit = fields.Float(required=True, validate=lambda w: 0 <= w <= 500)
    battery_capacity = fields.Float(required=True, validate=lambda b: 0 <= b <= 100)
    state = fields.Str(required=True, validate=lambda s: s in ["IDLE", "LOADING", "LOADED", "DELIVERING", "DELIVERED", "RETURNING"])


class MedicationSchema(Schema):

    '''Defines the medication scheme for validating'''
    
    name = fields.Str(required=True, validate=lambda n: n.isalnum() or '-' in n or '_' in n)
    weight = fields.Float(required=True, validate=lambda w: w >= 0)
    code = fields.Str(required=True, validate=lambda c: c.isupper() or '_' in c or c.isdigit())
    image = fields.Str(required=True)

# Class to manage resources
class DroneResource(Resource):

    '''Defines the class to manage the drone resources. Path to access these class /drones/<string:serial_number>'''
    
    drone_schema = DroneSchema()

    def get(self, serial_number=None):
    
        '''Obtain either all drones or a specific drone by its serial number'''
        
        if serial_number:
            # Obtain a medication from its serial number
            drone = Drone.query.filter_by(serial_number=serial_number).first()
            if drone:
                return {'serial_number': drone.serial_number, 'model': drone.model, 'weight_limit': drone.weight_limit,
                        'battery_capacity': drone.battery_capacity, 'state': drone.state}
            else:
                return {'message': 'Drone not found'}, 404
        else:
            # List of all Drones
            drones = Drone.query.all()
            if not drones:
                return {'message': 'There are no drones in the database'}

            drone_list = [{'serial_number': drone.serial_number, 'model': drone.model, 'weight_limit': drone.weight_limit,
                           'battery_capacity': drone.battery_capacity, 'state': drone.state} for drone in drones]
            return {'drones': drone_list}
            
    def post(self):
    
        '''Save a drone'''
        
        data = request.get_json()
        try:
            new_drone = self.drone_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        existing_drone = Drone.query.filter_by(serial_number=new_drone['serial_number']).first()
        if existing_drone:
            return {'message': 'There is already a drone with this serial number'}, 400
        
        # Check battery level before allowing the state change to LOADING
        if new_drone.get('state') == 'LOADING' and new_drone['battery_capacity'] >= 25:
            return {'message': 'Drone cannot be in LOADING state with battery level up 25%'}, 400

        
        db.session.add(Drone(**new_drone))
        db.session.commit()

        return {'message': 'Drone successfully created'}, 201


    def put(self, serial_number):
    
        '''Modify a drone based on its serial number'''
        
        data = request.get_json()
        try:
            updated_data = self.drone_schema.load(data, partial=True)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        drone = Drone.query.filter_by(serial_number=serial_number).first()
        
        if drone:           
            # Check battery level before allowing the state change to LOADING
            
            if updated_data.get('state') == 'LOADING' and drone.battery_capacity >= 25:
                return {'message': 'Drone cannot be in LOADING state with battery level up 25%'}, 400

            # Update Drone
            for key, value in updated_data.items():
                setattr(drone, key, value)
            db.session.commit()
                
            return {'message': 'Drone updated successfully'}
        else:
            return {'message': 'Drone not found'}, 404

    def delete(self, serial_number):
    
        '''Delete a drone based on its serial number'''
        drone = Drone.query.filter_by(serial_number=serial_number).first()

        if drone:
            # Search and delete in DroneMedication
            drone_medications = DroneMedication.query.filter_by(drone_id=drone.id).all()
            for drone_medication in drone_medications:
                db.session.delete(drone_medication)

            db.session.delete(drone)
            db.session.commit()
            return {'message': 'Drone deleted successfully'}
        else:
            return {'message': 'Drone not found'}, 404

class MedicationResource(Resource):

    '''Defines the class to manage the medication resources. Path to access these class /medications/<string:code>'''
    
    medication_schema = MedicationSchema()
            
    def get(self, code=None):
    
        '''Obtain either all medications or a specific medication by its code'''
        
        if code:
            # Obtain a medication from its serial number
            medication = Medication.query.filter_by(code=code).first()
            if medication:
                return {'name': medication.name, 'weight': medication.weight, 'code': medication.code, 'image': medication.image}
            else:
                return {'message': 'Medication not found'}, 404
        else:
            # Obtener la lista de todas las medicaciones
            medications = Medication.query.all()
            if not medications:
                return {'message': 'There are no medications in the database'}

            medication_list = [{'name': med.name, 'weight': med.weight, 'code': med.code, 'image': med.image} for med in medications]
            return {'medications': medication_list}
            
    def post(self):
    
        '''Save a Medication'''
        
        data = request.get_json()
        try:
            new_medication = self.medication_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        existing_medication = Medication.query.filter_by(code=new_medication['code']).first()
        if existing_medication:
            return {'message': 'There is already a Medication with this code'}, 400

        db.session.add(Medication(**new_medication))
        db.session.commit()

        return {'message': 'Medication created successfully'}, 201


    def put(self, code):
       
        '''Modify a medication based on its serial number'''
        
        data = request.get_json()
        try:
            updated_data = self.medication_schema.load(data, partial=True)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        medication = Medication.query.filter_by(code=code).first()

        if medication:
            # Update Medication
            for key, value in updated_data.items():
                setattr(medication, key, value)
            db.session.commit()
            return {'message': 'Medication updated successfully'}
        else:
            return {'message': 'Medication not found'}, 404

    def delete(self, code):
        
        '''Delete a medication based on its serial number'''
        
        medication = Medication.query.filter_by(code=code).first()
        if medication:
            # Buscar y eliminar en DroneMedication
            drone_medications = DroneMedication.query.filter_by(medication_id=medication.id).all()
            for drone_medication in drone_medications:
                db.session.delete(drone_medication)

            db.session.delete(medication)
            db.session.commit()
            return {'message': 'Medication deleted successfully'}
        else:
            return {'message': 'Medication not found'}, 404

class DroneWithMedicationResource(Resource):

    '''# Defines the class to load an existing drone with medications. Path to access these class /drones/with-medications'''
    
    drone_schema = DroneSchema()
    medication_schema = MedicationSchema()

    def post(self):
        '''Load a drone with the medications, for this it looks for its serial number and, if it exists, associates them and saves the medications.'''
        data = request.get_json()
        drone_data = data['drone']
        
        # Search existing drone by serial number
        existing_drone = Drone.query.filter_by(serial_number=drone_data['serial_number']).first()

        if not existing_drone:
            # If the drone does not exist, return an error
            return {'message': 'Drone not found with the given serial number'}, 404

        #Obtain all medications that will be charged
        medication_codes = data.get('medication_codes', [])
        existing_medications = Medication.query.filter(Medication.code.in_(medication_codes)).all()
        
        # Check if any medication does not exist
        if len(existing_medications) != len(medication_codes):
            non_existing_codes = set(medication_codes) - set(med.code for med in existing_medications)
            return {'message': f'The following medication codes do not exist: {", ".join(non_existing_codes)}'}, 404


        # Validate that the association does not previously exist in DroneMedication
        not_association = []
        massage = []
        for medication in existing_medications:
            
            existing_association = DroneMedication.query.filter_by(drone_id=existing_drone.id,
                                                                   medication_id=medication.id).first()
            if not existing_association:
                not_association.append(medication)
            else:
                massage.append(f'The medication {medication.name} is already associated with the drone')

        if massage:
            return {'message': massage}, 400

        # Validate the weight of medications
        total_weight = sum(med.weight for med in not_association)

        existing_association = db.session.query(Medication.name, Medication.weight, Medication.code,
                                                Medication.image). \
            join(DroneMedication, Medication.id == DroneMedication.medication_id). \
            filter(DroneMedication.drone_id == existing_drone.id).all()

        total_weight += sum(med.weight for med in existing_association)

        if total_weight > existing_drone.weight_limit:
            return {'message': 'Weight of medications exceeds drone limit'}, 400

        # Create the medications associated with the drone
        for medication in not_association:
            new_association = DroneMedication(drone_id=existing_drone.id, medication_id=medication.id)
            db.session.add(new_association)

        db.session.commit()

        return {'message': 'Drone with medications created successfully'}, 201
        
class DroneService(Resource):

    '''Defines the class to handle the additional functionality. Path to access these class /drones/service/<string:action>, /drones/service/<string:action>/<string:serial_number>'''
    
    def get(self, action, serial_number=None):
    
        '''method that loads the functionality depending on the requested service'''
        
        if action == 'loaded-medications':
            return self.get_loaded_medications(serial_number)
        elif action == 'available-drones':
            return self.get_available_drones()
        elif action == 'battery-level':
            return self.get_battery_level(serial_number)
        else:
            return {'message': 'Invalid action'}, 400

    def get_loaded_medications(self, serial_number):
    
        '''Get medications loaded on a drone from its serial number'''
        
        # Get the drone with the specified serial number
        drone = Drone.query.filter_by(serial_number=serial_number).first()
        
        if drone:
             # Query the medications loaded on the drone using the DroneMedication association table
            loaded_medications = db.session.query(Medication.name, Medication.weight, Medication.code, Medication.image). \
                join(DroneMedication, Medication.id == DroneMedication.medication_id). \
                filter(DroneMedication.drone_id == drone.id).all()

            # Convertir los resultados a una lista de diccionarios
            loaded_medications_list = [
                {'name': medication.name, 'weight': medication.weight, 'code': medication.code, 'image': medication.image}
                for medication in loaded_medications
            ]

            # Devolver la respuesta JSON
            return jsonify({'loaded_medications': loaded_medications_list})
        else:
            return {'message': 'Drone not found'}, 404

    def get_available_drones(self):
    
        '''Get the drones available'''
        
        # Query drones that are in the "IDLE" state
        available_drones = Drone.query.filter_by(state='IDLE').all()
        
        # Construct the response
        drone_list = [{'serial_number': drone.serial_number, 'model': drone.model, 'weight_limit': drone.weight_limit,
                       'battery_capacity': drone.battery_capacity, 'state': drone.state} for drone in available_drones]

        return {'available_drones': drone_list}

    def get_battery_level(self, serial_number):
    
        '''Get the battery of a drone from its serial number'''
        
        drone = Drone.query.filter_by(serial_number=serial_number).first()
        if drone:
            return {'serial_number': drone.serial_number, 'battery_capacity': drone.battery_capacity}
        else:
            return {'message': 'Drone not found'}, 404



# Add resource paths to the API
api.add_resource(DroneResource, '/drones', '/drones/<string:serial_number>')
api.add_resource(MedicationResource, '/medications', '/medications/<string:code>')
api.add_resource(DroneWithMedicationResource, '/drones/with-medications')
api.add_resource(DroneService, '/drones/service/<string:action>', '/drones/service/<string:action>/<string:serial_number>')

def main():
    with app.app_context():
        # Create tables only if they do not exist
        db.create_all()
    # Run the API
    app.run(debug=True)

if __name__ == '__main__':
    main()