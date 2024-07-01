from typing import Callable, Dict


# Example function
async def get_current_temperature(location: str, unit: str) -> str:
    return "72°F"


async def get_rain_probability(location: str) -> str:
    return "10%"

FUNCTION_MAP: Dict[str, Callable] = {
    "get_current_temperature": get_current_temperature,
    "get_rain_probability": get_rain_probability,
}


def get_function(name: str) -> Callable:
    return FUNCTION_MAP.get(name)
