from math import atan2, cos, radians, sin, sqrt

import requests
from requests.exceptions import RequestException

from logging_conf import logger


class Vehicle:
    def __init__(
        self,
        name: str,
        model: str,
        year: int,
        color: str,
        price: int,
        latitude: float,
        longitude: float,
        id: int | None = None,
    ):
        self.id = id
        self.name = name
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "year": self.year,
            "color": self.color,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def __repr__(self):
        return f"<Vehicle: {self.name} {self.model} {self.year} {self.color} {self.price}>"

    def __eq__(self, other):
        if isinstance(other, Vehicle):
            return (
                self.name == other.name
                and self.model == other.model
                and self.year == other.year
                and self.color == other.color
                and self.price == other.price
                and self.latitude == other.latitude
                and self.longitude == other.longitude
            )
        return False


class VehicleManager:

    def __init__(self, url: str):
        self.url = url
        self.logger = logger

    def get_vehicles(self) -> list[Vehicle | None]:
        try:
            response = requests.get(f"{self.url}/vehicles")
            response.raise_for_status()
            vehicles_data = response.json()
            return [Vehicle(**data) for data in vehicles_data]
        except RequestException as e:
            self.logger.error(f"An error occurred while fetching vehicles: {e}")
            return []

    def get_vehicle(self, vehicle_id: int) -> Vehicle | None:
        try:
            response = requests.get(f"{self.url}/vehicles/{vehicle_id}")
            response.raise_for_status()
            vehicle_data = response.json()
            return Vehicle(**vehicle_data)
        except RequestException as e:
            self.logger.error(f"An error occurred while fetching vehicle with id {vehicle_id}: {e}")
            return None

    def filter_vehicles(self, params: dict[str, str]) -> list[Vehicle]:
        try:
            vehicles_data = self.get_vehicles()
            filtered_vehicles = vehicles_data
            for key, value in params.items():
                filtered_vehicles = [vehicle for vehicle in filtered_vehicles if getattr(vehicle, key) == value]
            return filtered_vehicles
        except RequestException as e:
            self.logger.error(f"An error occurred while filtering vehicles: {e}")
            return []

    def add_vehicle(self, vehicle: Vehicle) -> Vehicle | None:
        try:
            response = requests.post(f"{self.url}/vehicles", data=vehicle.to_dict())
            response.raise_for_status()
            vehicle_data = response.json()
            return Vehicle(**vehicle_data)
        except RequestException as e:
            self.logger.error(f"An error occurred while adding vehicle: {e}")
            return None

    def update_vehicle(self, vehicle: Vehicle) -> Vehicle | None:
        try:
            if not vehicle.id:
                raise ValueError("Vehicle ID must be provided for updating.")
            response = requests.put(f"{self.url}/vehicles/{vehicle.id}", data=vehicle.to_dict())
            response.raise_for_status()
            vehicle_data = response.json()
            return Vehicle(**vehicle_data)
        except (RequestException, ValueError) as e:
            self.logger.error(f"An error occurred while updating vehicle: {e}")
            return None

    def delete_vehicle(self, vehicle_id: int) -> bool:
        try:
            response = requests.delete(f"{self.url}/vehicles/{vehicle_id}")
            response.raise_for_status()
            return response.status_code == 204
        except RequestException as e:
            self.logger.error(f"An error occurred while deleting vehicle with id {vehicle_id}: {e}")
            return False

    def get_distance(self, id1: int, id2: int) -> float | None:
        try:
            vehicle1 = self.get_vehicle(id1)
            vehicle2 = self.get_vehicle(id2)
            if vehicle1 and vehicle2:
                return self._calculate_distance(
                    vehicle1.latitude,
                    vehicle1.longitude,
                    vehicle2.latitude,
                    vehicle2.longitude,
                )
            else:
                return None
        except RequestException as e:
            self.logger.error(f"An error occurred while calculating distance between vehicles: {e}")
            return None

    def get_nearest_vehicle(self, id: int) -> Vehicle | None:
        try:
            vehicles = self.get_vehicles()
            ind = next((index for index, vehicle in enumerate(vehicles) if vehicle.id == id), None)

            if ind is not None:
                current_vehicle = vehicles.pop(ind)

            if vehicles and current_vehicle:
                nearest_vehicle = min(
                    vehicles,
                    key=lambda vehicle: self._calculate_distance(
                        current_vehicle.latitude,
                        current_vehicle.longitude,
                        vehicle.latitude,
                        vehicle.longitude,
                    ),
                )
                return nearest_vehicle
            else:
                return None
        except RequestException as e:
            self.logger.error(f"An error occurred while finding nearest vehicle: {e}")
            return None

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0  # approximate radius of Earth in km

        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c * 1000  # in meters
        return distance
