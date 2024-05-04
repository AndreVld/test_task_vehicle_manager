import json
import unittest

from vehicle_manager import Vehicle, VehicleManager


class TestVehicleManager(unittest.TestCase):
    def setUp(self):
        self.manager = VehicleManager(url="https://test.tspb.su/test-task")
        with open("vehicles.json", "r") as f:
            vehicles_data = json.load(f)
            self.all_vehicles = [Vehicle(**data) for data in vehicles_data]

    def test_get_vehicles(self):

        vehicles = self.manager.get_vehicles()
        self.assertIsInstance(vehicles, list)
        if vehicles:
            for vehicle in vehicles:
                self.assertIsInstance(vehicle, Vehicle)

    def test_get_vehicle(self):
        test_vehicle_id = 14
        vehicle = self.manager.get_vehicle(vehicle_id=test_vehicle_id)

        if vehicle is not None:
            self.assertIsInstance(vehicle, Vehicle)

    def test_filter_by_attribute(self):
        test_cases = [
            ("name", "Toyota"),
            ("year", 2015),
            ("color", "red"),
            ("price", 21000),
        ]

        for attribute, value in test_cases:
            filter_params = {attribute: value}
            expected_result = [vehicle for vehicle in self.all_vehicles if getattr(vehicle, attribute) == value]
            filtered_vehicles = self.manager.filter_vehicles(filter_params)
            self.assertEqual(len(filtered_vehicles), len(expected_result))
            for vehicle1, vehicle2 in zip(filtered_vehicles, expected_result):
                self.assertEqual(vehicle1, vehicle2)

    def test_add_vehicle(self):
        test_vehicle = Vehicle(
            name="TestCamry",
            model="TestToyota",
            year=2014,
            color="TestWhite",
            price=10000,
            latitude=37.621676,
            longitude=55.753332,
        )
        added_vehicle = self.manager.add_vehicle(test_vehicle)

        self.assertIsInstance(added_vehicle, Vehicle)

        self.assertEqual(added_vehicle, test_vehicle)

    def test_update_vehicle(self):

        test_vehicle = Vehicle(
            id=1,
            name="Camry",
            model="Toyota",
            year=2014,
            color="White",
            price=10000,
            latitude=37.621676,
            longitude=55.753332,
        )

        updated_vehicle = self.manager.update_vehicle(test_vehicle)

        self.assertIsInstance(updated_vehicle, Vehicle)
        self.assertEqual(updated_vehicle, test_vehicle)

    def test_delete_vehicle(self):
        test_vehicle_id = 1

        deletion_result = self.manager.delete_vehicle(vehicle_id=test_vehicle_id)

        self.assertIsInstance(deletion_result, bool)
        self.assertTrue(deletion_result)

    def test_get_distance(self):
        test_vehicle_id1 = 1
        test_vehicle_id2 = 2

        distance = self.manager.get_distance(id1=test_vehicle_id1, id2=test_vehicle_id2)
        self.assertIsInstance(distance, (float, type(None)))

    def test_get_nearest_vehicle(self):

        test_vehicle_id = 1
        nearest_vehicle = self.manager.get_nearest_vehicle(id=test_vehicle_id)
        self.assertIsInstance(nearest_vehicle, Vehicle)


if __name__ == "__main__":
    unittest.main()
