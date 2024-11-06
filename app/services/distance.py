import math


class DistanceCalculator:
    EARTH_RADIUS_KM = 6371

    async def calculate_distance(
        self,
        latitude_first: float,
        longitude_first: float,
        latitude_second: float,
        longitude_second: float
    ) -> float:
        latitude_first, longitude_first, latitude_second, longitude_second = \
            map(
                math.radians, [
                    latitude_first,
                    longitude_first,
                    latitude_second,
                    longitude_second]
            )
        delta_lambda = longitude_second - longitude_first
        central_angle = math.acos(
            math.sin(latitude_first) * math.sin(latitude_second) +
            math.cos(latitude_first) * math.cos(latitude_second) *
            math.cos(delta_lambda)
        )
        distance = DistanceCalculator.EARTH_RADIUS_KM * central_angle
        return distance

    async def is_within_distance(
        self,
        latitude_first: float,
        longitude_first: float,
        latitude_second: float,
        longitude_second: float,
        max_distance_km: float
    ) -> bool:

        distance = await self.calculate_distance(
            latitude_first,
            longitude_first,
            latitude_second,
            longitude_second)
        return True if distance <= max_distance_km else False
