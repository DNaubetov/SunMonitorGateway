import datetime
from typing import Optional
from fastapi import FastAPI, Query, Path
from connect import Settings
import uvicorn
import requests
import enum
from fastapi.middleware.cors import CORSMiddleware

settings = Settings()

ip_list = {
    'JSC_TPP': settings.JSC_TPP,
    'TASHKENT_TTC': settings.TASHKENT_TTC,
    'SIRDARYA_TPP': settings.SIRDARYA_TPP,
    'MUBAREK_TPP': settings.MUBAREK_TPP
}


class Location(enum.Enum):
    JSC_TPP = 'JSC_TPP'
    TASHKENT_TTC = 'TASHKENT_TTC'
    SIRDARYA_TPP = 'SIRDARYA_TPP'
    MUBAREK_TPP = 'MUBAREK_TPP'
    ALL = 'ALL'


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_data(url: str) -> dict:
    """Асинхронное получение данных с заданного URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


def build_endpoint(last: bool, year: Optional[int], month: Optional[int], day: Optional[int]) -> str:
    """Построение конечного пути API запроса."""
    if last:
        return '/data/chart/last/all/'
    if year and month and day:
        return f'/data/chart/day/all/{year}-{month:02d}-{day:02d}'
    if year and month:
        return f'/data/chart/month/all/{year}/{month:02d}'
    if year:
        return f'/data/chart/year/all/{year}'
    return ""


@app.get('/data/chart/{location}/')
async def get_all_chart(
        location: Location = Location.JSC_TPP,
        last: Optional[bool] = None,
        year: Optional[int] = Query(None, ge=2024, le=2100, description="Год в формате ГГГГ"),
        month: Optional[int] = Query(None, ge=1, le=12, description="Месяц в формате ММ"),
        day: Optional[int] = Query(None, ge=1, le=31, description="День в формате ДД")):
    """Получение данных для графиков по локации."""
    endpoint = build_endpoint(last, year, month, day)
    if not endpoint:
        return {"error": "Invalid parameters"}

    if location == Location.ALL:
        # Запрос данных со всех IP
        return [await fetch_data(f'http://{ip}:8080{endpoint}') for ip in ip_list.values()]

    # Запрос данных с конкретной локации
    ip = ip_list.get(location.value)
    return await fetch_data(f'http://{ip}:8080{endpoint}')


@app.get("/{location}/data/chart/last/all/", tags=['all inv last data'])
async def read_last_data(location: Location):
    endpoint = '/data/chart/last/all/'

    if location == Location.ALL:
        # Запрос данных со всех IP
        return [await fetch_data(f'http://{ip}:8080{endpoint}') for ip in ip_list.values()]

        # Запрос данных с конкретной локации
    ip = ip_list.get(location.value)
    return await fetch_data(f'http://{ip}:8080{endpoint}')


@app.get("/{location}/data/chart/year/all/{year}", tags=['all inv chart'])
async def data_chart_for_year_all_inverters(location: Location,
                                            year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ")):
    endpoint = f'/data/chart/year/all/{year}'

    if location == Location.ALL:
        # Запрос данных со всех IP
        return [await fetch_data(f'http://{ip}:8080{endpoint}') for ip in ip_list.values()]

        # Запрос данных с конкретной локации
    ip = ip_list.get(location.value)
    return await fetch_data(f'http://{ip}:8080{endpoint}')


@app.get("/{location}/data/chart/month/all/{year}/{month}", tags=['all inv chart'])
async def data_chart_for_month_all_inverters(
        location: Location,
        year: int = Path(..., ge=2000, le=2100, description="Год в формате ГГГГ"),
        month: int = Path(..., ge=1, le=12, description="Месяц в формате ММ")):
    endpoint = f'/data/chart/month/all/{year}/{month:02d}'

    if location == Location.ALL:
        # Запрос данных со всех IP
        return [await fetch_data(f'http://{ip}:8080{endpoint}') for ip in ip_list.values()]

        # Запрос данных с конкретной локации
    ip = ip_list.get(location.value)
    return await fetch_data(f'http://{ip}:8080{endpoint}')


@app.get("/{location}/data/chart/day/all/{target_date}",
         summary="Ручка для получения всех данных за target_date, со всех инверторов",
         tags=['all inv chart'])
async def data_chart_for_day_all_inverters(location: Location,
                                           target_date: datetime.date = Path(...,
                                                                             description="Дата в формате ГГГГ-ММ-ДД")):
    endpoint = f'/data/chart/day/all/{target_date}'

    if location == Location.ALL:
        # Запрос данных со всех IP
        return [await fetch_data(f'http://{ip}:8080{endpoint}') for ip in ip_list.values()]

        # Запрос данных с конкретной локации
    ip = ip_list.get(location.value)
    return await fetch_data(f'http://{ip}:8080{endpoint}')


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8888, reload=True)
