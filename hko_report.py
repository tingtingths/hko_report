#!/usr/bin/env python3
import json
import re
from argparse import ArgumentParser

import rich
from requests_futures.sessions import FuturesSession
from rich.console import Console
from rich.table import Table

from json_helper import *

api_url = "http://www.hko.gov.hk/wxinfo/json/one_json_uc.xml"
api_url_eng = "http://www.hko.gov.hk/wxinfo/json/one_json.xml"
warning_url = "http://www.hko.gov.hk/wxinfo/json/warnsumc.xml"
warning_url_eng = "http://www.hko.gov.hk/wxinfo/json/warnsum.xml"
info = OrderedDict()
info_map = OrderedDict([
    ("Obs. Time", "RHRREAD/FormattedObsTime"),
    ("Air temperature", ("hko/Temperature", "+str:°C")),
    ("Max temperature", ("hko/HomeMaxTemperature", "+str:°C")),
    ("Min temperature", ("hko/HomeMinTemperature", "+str:°C")),
    ("Relative humidity", ("hko/RH", "+str:%")),
    ("UV Index", "RHRREAD/UVIndex"),
    ("UV Intensity", "RHRREAD/Intensity"),
    ("General Situation and Forecast",
     ("+str:\n  ", "FLW/GeneralSituation", "+str:\n  ", "FLW/ForecastDesc", "+str:\n  ", "FLW/OutlookContent")),
])
astron_info = OrderedDict()
astron_info_map = OrderedDict([
    ("Lunar date", "CMN/LunarDate"),
    ("Sunrise", "CMN/sunriseTime"),
    ("Sunset", "CMN/sunsetTime"),
    ("Moonrise", "CMN/moonriseTime"),
    ("Moonset", "CMN/moonsetTime")
])
tide_info = []
tide_info_map = OrderedDict([
    ("root", "CMN/tide"),
    ("Tide", "type"),
    ("Tide time", "time"),
    ("Height", ("height", "+str:m"))
])
nine_day_map = OrderedDict([
    ("root", "F9D/WeatherForecast"),
    ("Date", "ForecastDate"),
    ("Day", "WeekDay"),
    ("Temperature", ("ForecastMintemp", "+str:°C - ", "ForecastMaxtemp", "+str:°C")),
    ("Relative humidity", ("ForecastMinrh", "+str:% - ", "ForecastMaxrh", "+str:%")),
    ("Wind", "ForecastWind"),
    ("Weather", "ForecastWeather")
])
nine_day_info = []
warning_map = OrderedDict([
    ("Warning", ("Name", "+str: - ", "Type")),
    ("_action", "ActionCode")
])
warning_info = []
translation = {
    "Air temperature": "氣溫",
    "Temperature": "氣溫",
    "Max temperature": "最高氣溫",
    "Min temperature": "最低氣溫",
    "Relative humidity": "相對濕度",
    "UV Index": "紫外線指數",
    "UV Intensity": "紫外線強度",
    "Obs. Time": "觀測時間",
    "General Situation and Forecast": "天氣概況及預報",
    "Max relative humidity": "最高相對濕度",
    "Min relative humidity": "最低相對濕度",
    "Wind": "風",
    "Day": "星期",
    "Date": "日期",
    "Weather": "天氣",
    "Lunar date": "農曆",
    "Sunrise": "日出",
    "Sunset": "日落",
    "Moonrise": "月出",
    "Moonset": "月落",
    "Tide": "潮汐",
    "Tide time": "潮汐時間",
    "Height": "高度",
    "Warning": "警告",
    'Sunday': '日',
    'Monday': '一',
    'Tuesdays': '二',
    'Wednesday': '三',
    'Thursday': '四',
    'Friday': '五',
    'Saturday': '六',
    '9-Day Forecast': '九天天氣預報',
}
weekdays = [
    'Sunday',
    'Monday',
    'Tuesdays',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
]


def print_info(root, translate=False, ignore=[], highlight=False):
    for k in root.keys():
        if k not in ignore:
            v = root[k]
            if translate and k in translation:
                k = translation[k]
            if translate and v in translation:
                v = translation[v]
            if highlight:
                rich.print("[bold red]" + k + ": " + v + "[/bold red]")
            else:
                print(k + ": " + v)


def print_array(info, translate=True):
    for d in info:
        print()
        print_info(d, translate)


def print_table(info, title='', translate=True):
    if info is None or len(info) == 0:
        return

    table = Table(title=title)
    # build column
    for column in info[0].keys():
        if translate and column in translation.keys():
            column = translation[column]
        table.add_column(header=column, overflow='fold')
    for d in info:
        values = [translation[v] if translate and v in translation.keys() else v for v in d.values()]
        table.add_row(*values)
    # print
    Console().print(table)


if __name__ == "__main__":
    parser = ArgumentParser(description="Print weather report from Hong Kong Observatory.")
    parser.add_argument("-l", "--latest", action="store_true", help="show latest general weather information")
    parser.add_argument("-9", "--nine-days", action="store_true", help="show 9 days weather forecast")
    parser.add_argument("-a", "--astron", action="store_true", help="show astronomical observation")
    parser.add_argument("--unrich", action="store_true", help="disable pretty print")
    parser.add_argument("--all", action="store_true", help="show all information")
    parser.add_argument("--english", action="store_true", help="show information in English")
    args = parser.parse_args()

    translate = not args.english
    if not translate:
        api_url = api_url_eng
        warning_url = warning_url_eng

    # multiple requests at once
    session = FuturesSession()
    req_api = session.get(api_url)
    req_warn = session.get(warning_url)
    # general info
    json_s = req_api.result().content.decode("utf8")
    json_dict = json.loads(json_s)
    infoj = JsonHelper(json_dict)
    # warning info
    warn_json = req_warn.result().content.decode("utf8")
    result = re.match(r".*?({.*}).*", warn_json)
    if result:
        warn_json_dict = json.loads(result.group(1))

    if args.latest or args.all:
        info = infoj.build_dict(info_map)
        print_info(info, translate)
        if warn_json_dict:
            for w in warn_json_dict:
                warnj = JsonHelper(warn_json_dict[w])
                d = warnj.build_dict(warning_map)
                if d["_action"] == "ISSUE":
                    print_info(d, translate, ["_action"], True and not args.unrich)
    if args.astron or args.all:
        astron_info = infoj.build_dict(astron_info_map)
        print_info(astron_info, translate)
        tide_info = infoj.build_array(tide_info_map)
        print_array(tide_info, translate)
    if args.nine_days or args.all:
        nine_day_info = infoj.build_array(nine_day_map)
        for day_info in nine_day_info:
            day_info['Day'] = weekdays[int(day_info['Day'])]
        if args.unrich:
            print_array(nine_day_info, translate)
        else:
            print_table(nine_day_info,
                        title=translation['9-Day Forecast'] if translate else '9-Day Forecast',
                        translate=translate)
