"""
天气查询 MCP 服务器
使用 wttr.in 免费 API，无需 API Key
"""

import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

WTTR_BASE = "https://wttr.in"

WMO_CODES = {
    0: "晴天", 1: "基本晴朗", 2: "局部多云", 3: "阴天",
    45: "有雾", 48: "结冰雾",
    51: "小毛毛雨", 53: "中毛毛雨", 55: "大毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "冰粒",
    80: "小阵雨", 81: "中阵雨", 82: "大阵雨",
    85: "小阵雪", 86: "大阵雪",
    95: "雷暴", 96: "雷暴伴小冰雹", 99: "雷暴伴大冰雹",
}


def _wind_direction(degrees: int) -> str:
    directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    return directions[round(degrees / 45) % 8]


@mcp.tool()
async def get_current_weather(city: str) -> str:
    """
    查询指定城市的当前天气。
    
    参数:
        city: 城市名称，支持中文、英文或拼音，例如 "北京"、"Beijing"、"Shanghai"
    
    返回当前气温、体感温度、天气状况、湿度、风速风向、能见度等信息。
    """
    url = f"{WTTR_BASE}/{city}"
    params = {
        "format": "j1",
        "lang": "zh",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            return f"请求失败（HTTP {e.response.status_code}），请检查城市名称是否正确。"
        except Exception as e:
            return f"网络错误：{e}"

    current = data["current_condition"][0]
    area = data.get("nearest_area", [{}])[0]

    area_name = (
        area.get("areaName", [{}])[0].get("value", city)
        if area.get("areaName") else city
    )
    country = (
        area.get("country", [{}])[0].get("value", "")
        if area.get("country") else ""
    )

    temp_c = current["temp_C"]
    feels_like_c = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_kmph = current["windspeedKmph"]
    wind_deg = int(current["winddirDegree"])
    visibility_km = current["visibility"]
    weather_desc = current.get("lang_zh", [{}])
    if weather_desc:
        desc = weather_desc[0].get("value", current["weatherDesc"][0]["value"])
    else:
        desc = current["weatherDesc"][0]["value"]
    uv_index = current.get("uvIndex", "N/A")
    cloud_cover = current.get("cloudcover", "N/A")
    pressure = current.get("pressure", "N/A")
    precip_mm = current.get("precipMM", "0")

    location_str = f"{area_name}, {country}" if country else area_name

    return (
        f"📍 {location_str} 当前天气\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌡️  气温：{temp_c}°C（体感 {feels_like_c}°C）\n"
        f"🌤️  天气：{desc}\n"
        f"💧 湿度：{humidity}%\n"
        f"💨 风速：{wind_kmph} km/h，风向：{_wind_direction(wind_deg)}（{wind_deg}°）\n"
        f"👁️  能见度：{visibility_km} km\n"
        f"☁️  云量：{cloud_cover}%\n"
        f"🌡️  气压：{pressure} hPa\n"
        f"🌧️  降水量：{precip_mm} mm\n"
        f"☀️  紫外线指数：{uv_index}"
    )


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    查询指定城市未来的天气预报。
    
    参数:
        city: 城市名称，支持中文、英文或拼音，例如 "北京"、"London"
        days: 预报天数，1-3 天（默认 3 天）
    
    返回每天的最高/最低温度、天气状况、降水概率、日出日落时间等信息。
    """
    days = max(1, min(days, 3))

    url = f"{WTTR_BASE}/{city}"
    params = {
        "format": "j1",
        "lang": "zh",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            return f"请求失败（HTTP {e.response.status_code}），请检查城市名称是否正确。"
        except Exception as e:
            return f"网络错误：{e}"

    area = data.get("nearest_area", [{}])[0]
    area_name = (
        area.get("areaName", [{}])[0].get("value", city)
        if area.get("areaName") else city
    )
    country = (
        area.get("country", [{}])[0].get("value", "")
        if area.get("country") else ""
    )
    location_str = f"{area_name}, {country}" if country else area_name

    forecast_days = data.get("weather", [])[:days]
    if not forecast_days:
        return "未能获取预报数据，请稍后重试。"

    lines = [f"📍 {location_str} 天气预报（{days} 天）", "━━━━━━━━━━━━━━━━━━━━"]

    for day_data in forecast_days:
        date = day_data["date"]
        max_temp = day_data["maxtempC"]
        min_temp = day_data["mintempC"]
        sunrise = day_data.get("astronomy", [{}])[0].get("sunrise", "N/A")
        sunset = day_data.get("astronomy", [{}])[0].get("sunset", "N/A")

        hourly = day_data.get("hourly", [])
        descriptions = []
        rain_chances = []
        for h in hourly:
            zh_desc = h.get("lang_zh", [{}])
            if zh_desc:
                descriptions.append(zh_desc[0].get("value", ""))
            rain_chances.append(int(h.get("chanceofrain", 0)))

        main_desc = max(set(descriptions), key=descriptions.count) if descriptions else "N/A"
        avg_rain = sum(rain_chances) // len(rain_chances) if rain_chances else 0

        lines.append(
            f"\n📅 {date}\n"
            f"   🌡️  {min_temp}°C ~ {max_temp}°C\n"
            f"   🌤️  {main_desc}\n"
            f"   🌧️  降雨概率：{avg_rain}%\n"
            f"   🌅 日出：{sunrise}  🌇 日落：{sunset}"
        )

    return "\n".join(lines)


@mcp.tool()
async def get_weather_by_coordinates(latitude: float, longitude: float) -> str:
    """
    根据经纬度查询当前天气。
    
    参数:
        latitude: 纬度，例如 39.9042（北京）
        longitude: 经度，例如 116.4074（北京）
    
    返回该坐标位置的当前天气信息。
    """
    location = f"{latitude},{longitude}"
    url = f"{WTTR_BASE}/{location}"
    params = {
        "format": "j1",
        "lang": "zh",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            return f"请求失败（HTTP {e.response.status_code}），请检查坐标是否正确。"
        except Exception as e:
            return f"网络错误：{e}"

    current = data["current_condition"][0]
    area = data.get("nearest_area", [{}])[0]

    area_name = (
        area.get("areaName", [{}])[0].get("value", location)
        if area.get("areaName") else location
    )
    country = (
        area.get("country", [{}])[0].get("value", "")
        if area.get("country") else ""
    )

    temp_c = current["temp_C"]
    feels_like_c = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_kmph = current["windspeedKmph"]
    wind_deg = int(current["winddirDegree"])
    visibility_km = current["visibility"]
    weather_desc = current.get("lang_zh", [{}])
    if weather_desc:
        desc = weather_desc[0].get("value", current["weatherDesc"][0]["value"])
    else:
        desc = current["weatherDesc"][0]["value"]
    pressure = current.get("pressure", "N/A")
    precip_mm = current.get("precipMM", "0")

    location_str = f"{area_name}, {country}" if country else area_name

    return (
        f"📍 {location_str}（{latitude}, {longitude}）当前天气\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌡️  气温：{temp_c}°C（体感 {feels_like_c}°C）\n"
        f"🌤️  天气：{desc}\n"
        f"💧 湿度：{humidity}%\n"
        f"💨 风速：{wind_kmph} km/h，风向：{_wind_direction(wind_deg)}（{wind_deg}°）\n"
        f"👁️  能见度：{visibility_km} km\n"
        f"🌡️  气压：{pressure} hPa\n"
        f"🌧️  降水量：{precip_mm} mm"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
