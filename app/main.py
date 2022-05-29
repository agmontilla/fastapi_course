from http import HTTPStatus
from typing import Any, List, Optional

import requests as rq
from fastapi import FastAPI
from pydantic import BaseModel, validator

WORLD_TIME_API = "http://worldtimeapi.org/api/timezone"
AVAILABLE_TIMEZONES = tuple(rq.get(WORLD_TIME_API).json())

app = FastAPI()


class City(BaseModel):
    name: str
    timezone: str

    @validator("timezone")
    def validate_timezone(cls, v: str) -> str:
        if v not in AVAILABLE_TIMEZONES:
            raise ValueError(f"{v} is not a valid timezone")
        return v


class CityDetails(City):
    datetimezone: Optional[str] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


db: List[City] = [
    City(name="London", timezone="Europe/London"),
    City(name="Paris", timezone="Europe/Paris"),
]


@app.get("/cities", response_model=List[CityDetails])
async def get_cities() -> List[CityDetails]:
    response: List = []
    for city in db:
        timezone_entity = rq.get(WORLD_TIME_API + "/" + city.timezone).json()
        city_details = CityDetails(
            name=city.name,
            timezone=city.timezone,
            datetimezone=timezone_entity["datetime"],
        )
        response.append(city_details)
    return response


@app.get("/cities/{id}", response_model=CityDetails)
async def get_city(id: int) -> CityDetails:
    city = db[id - 1]
    timezone_entity = rq.get(WORLD_TIME_API + "/" + city.timezone).json()
    city_details = CityDetails(
        name=city.name,
        timezone=city.timezone,
        datetimezone=timezone_entity["datetime"],
    )
    return city_details


@app.post("/cities", status_code=HTTPStatus.CREATED, response_model=City)
async def create_city(city: City) -> City:
    db.append(city)
    return city


@app.delete("/cities/{id}", status_code=HTTPStatus.NO_CONTENT)
def delete_city(id: int) -> None:
    db.pop(id - 1)
    return
