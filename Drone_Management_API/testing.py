import unittest
from Drone_Management_API import app  # Importa tu aplicación Flask


drones_test = [{'serial_number': 'DRN1', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'}, {'serial_number': 'DRN2', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'}, {'serial_number': 'DRN3', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'}, {'serial_number': 'DRN4', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'}, {'serial_number': 'DRN5', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'}]
drone_test ={
    "serial_number": "SN123",
    "model": "Lightweight",
    "weight_limit": 10.0,
    "battery_capacity": 80.0,
    "state": "IDLE"
}

medications_test = [{'name': 'Medication1', 'weight': 5.0, 'code': 'MED1', 'image': 'example_image.jpg'}, {'name': 'Medication2', 'weight': 5.0, 'code': 'MED2', 'image': 'example_image.jpg'}, {'name': 'Medication3', 'weight': 5.0, 'code': 'MED3', 'image': 'example_image.jpg'}, {'name': 'Medication4', 'weight': 5.0, 'code': 'MED4', 'image': 'example_image.jpg'}, {'name': 'Medication5', 'weight': 5.0, 'code': 'MED5', 'image': 'example_image.jpg'}]
medication_test = {
     "name": "Med1",
     "weight": 10.0,
     "code": "MED123",
     "image": "med1.jpg"
}

class testDroneResource(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_droneresource_getall(self):
        response = self.app.get('/drones')
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data['drones'], drones_test)

    def test_droneresource_get(self):
        response = self.app.get('/drones/DRN1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, drones_test[0])

    def test_droneresource_get_notfound(self):
        response = self.app.get('/drones/DRN8')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['message'], 'Drone not found')

    def test_droneresource_post(self):
        response = self.app.post('/drones', json=drone_test)
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'Drone successfully created')

    def test_droneresource_post_error_exist(self):
        response = self.app.post('/drones', json=drone_test)
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'There is already a drone with this serial number')

    def test_droneresource_put(self):
        response = self.app.put('/drones/SN123', json={"state": "RETURNING"})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Drone updated successfully')

    def test_droneresource_put_notfound(self):
        response = self.app.put('/drones/SN126', json={"state": "RETURNING"})
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Drone not found')

    def test_droneresource_put(self):
        response = self.app.put('/drones/SN123', json={"state": "LOADING"})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Drone cannot be in LOADING state with battery level up 25%')

    def test_droneresource_delete(self):
        response = self.app.delete('/drones/SN123')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Drone deleted successfully')

    def test_droneresource_delete_notfound(self):
        response = self.app.delete('/drones/SN123')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Drone not found')

class testMedicationResource(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_medicationresource_getall(self):
        response = self.app.get('/medications')
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data['medications'], medications_test)

    def test_medicationresource_get(self):
        response = self.app.get('/medications/MED1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, medications_test[0])

    def test_medicationresource_get_notfound(self):
        response = self.app.get('/medications/DRN8')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['message'], 'Medication not found')

    def test_medicationresource_post(self):
        response = self.app.post('/medications', json=medication_test)
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'Medication created successfully')

    def test_medicationresource_post_error_exist(self):
        response = self.app.post('/medications', json=medication_test)
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'There is already a Medication with this code')

    def test_medicationresource_put(self):
        response = self.app.put('/medications/MED123', json={"weight": 15.0})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Medication updated successfully')

    def test_medicationresource_put_notfound(self):
        response = self.app.put('/medications/MED156', json={"weight": 15.0})
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Medication not found')

    def test_medicationresource_delete(self):
        response = self.app.delete('/medications/MED123')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Medication deleted successfully')

    def test_medicationresource_delete_notfound(self):
        response = self.app.delete('/medications/MED123')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Medication not found')

class testDroneWithMedicationResource(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_droneMedicationresource_dronenotfound(self):
        drone_with_medication_data = {
            "drone": {
                "serial_number": "DRN80",
            },
            "medication_codes": ["MED1", "MED2"]
        }
        response = self.app.post('/drones/with-medications',json=drone_with_medication_data)
        self.assertEqual(response.status_code,404)
        data = response.get_json()
        self.assertEqual(data['message'], 'Drone not found with the given serial number')

    def test_droneMedicationresourcemedicationnotfound(self):
        drone_with_medication_data = {
            "drone": {
                "serial_number": "SN123",
            },
            "medication_codes": ["MED9"]
        }
        response = self.app.post('/drones/with-medications',json=drone_with_medication_data)
        self.assertEqual(response.status_code,404)
        data = response.get_json()
        self.assertEqual(data['message'], 'The following medication codes do not exist: MED9')


    def test_droneMedicationresource(self):
        drone_with_medication_data = {
            "drone": {
                "serial_number": "SN123",
            },
            "medication_codes": ["MED1", "MED2"]
        }
        response = self.app.post('/drones/with-medications',json=drone_with_medication_data)
        self.assertEqual(response.status_code,201)
        data = response.get_json()
        self.assertEqual(data['message'], 'Drone with medications created successfully')

        response = self.app.get('/drones/service/loaded-medications/SN123')
        medicatio_in_drone = [{
            'code': 'MED1', 'image': 'example_image.jpg', 'name': 'Medication1', 'weight': 5.0}, \
            {'code': 'MED2', 'image': 'example_image.jpg', 'name': 'Medication2', 'weight': 5.0}]
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['loaded_medications'], medicatio_in_drone)

    def test_droneMedicationresource_medication_Weight(self):
        drone_with_medication_data = {
            "drone": {
                "serial_number": "SN123",
            },
            "medication_codes": ["MED3", "MED4"]
        }
        response = self.app.post('/drones/with-medications',json=drone_with_medication_data)
        self.assertEqual(response.status_code,400)
        data = response.get_json()
        self.assertEqual(data['message'], 'Weight of medications exceeds drone limit')


    def test_droneMedicationresource_associated(self):
        drone_with_medication_data = {
            "drone": {
                "serial_number": "SN123",
            },
            "medication_codes": ["MED1"]
        }
        response = self.app.post('/drones/with-medications',json=drone_with_medication_data)
        self.assertEqual(response.status_code,400)
        data = response.get_json()
        self.assertEqual(data['message'][0], 'The medication Medication1 is already associated with the drone')

class testDroneService(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_DroneService_erroraction(self):
        response = self.app.get('/drones/service/test')
        self.assertEqual(response.status_code,400)
        data = response.get_json()
        self.assertEqual(data['message'], 'Invalid action')

    def test_DroneService_loaded_medications_notfound(self):
        response = self.app.get('/drones/service/loaded-medications/DRN9')
        self.assertEqual(response.status_code,404)
        data = response.get_json()
        self.assertEqual(data['message'], 'Drone not found')


    def test_DroneService_get_available_drones(self):
        response = self.app.get('/drones/service/available-drones')
        self.assertEqual(response.status_code,200)

        available_drones = [{'serial_number': 'DRN1', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'},
                            {'serial_number': 'DRN2', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'},
                            {'serial_number': 'DRN3', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'},
                            {'serial_number': 'DRN4', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'},
                            {'serial_number': 'DRN5', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'},
                            {'serial_number': 'SN123', 'model': 'Lightweight', 'weight_limit': 10.0, 'battery_capacity': 80.0, 'state': 'IDLE'}]
        data = response.get_json()
        self.assertEqual(data['available_drones'], available_drones)

    def test_DroneService_get_battery_level(self):
        response = self.app.get('/drones/service/battery-level/DRN1')
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data, {'serial_number': 'DRN1', 'battery_capacity': 80.0})

    def test_DroneService_get_battery_level_notfound(self):
        response = self.app.get('/drones/service/battery-level/DRN9')
        self.assertEqual(response.status_code,404)
        data = response.get_json()
        self.assertEqual(data['message'], 'Drone not found')

if __name__ == '__main__':
    unittest.main()