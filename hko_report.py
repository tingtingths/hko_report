import sys
import datetime
from collections import OrderedDict
from urllib.request import urlopen
from json_helper import *


api_url = "http://www.hko.gov.hk/wxinfo/json/one_json_uc.xml"
api_url_eng = "http://www.hko.gov.hk/wxinfo/json/one_json.xml"
info = OrderedDict()
info_map = OrderedDict([
	("Obs. Time", "RHRREAD/FormattedObsTime"),
	("Air temperature", ("hko/Temperature", "+str:°C")),
	("Max temperature", ("hko/HomeMaxTemperature", "+str:°C")),
	("Min temperature", ("hko/HomeMinTemperature", "+str:°C")),
	("Relative humidity", ("hko/RH", "+str:%")),
	("UV Index", "RHRREAD/UVIndex"),
	("UV Intensity", "RHRREAD/Intensity"),
	("General Situation and Forecast", ("+str:\n  ", "FLW/GeneralSituation", "+str:\n  ", "FLW/ForecastDesc", "+str:\n  ", "FLW/OutlookContent")),
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
translation = {
	"Air temperature":"氣溫",
	"Temperature":"氣溫",
	"Max temperature":"最高氣溫",
	"Min temperature":"最低氣溫",
	"Relative humidity":"相對濕度",
	"UV Index":"紫外線指數",
	"UV Intensity":"紫外線強度",
	"Obs. Time":"觀測時間",
	"General Situation and Forecast":"天氣概況及預報",
	"Max relative humidity":"最高相對濕度",
	"Min relative humidity":"最低相對濕度",
	"Wind":"風",
	"Day":"星期",
	"Date":"日期",
	"Weather":"天氣",
	"Lunar date":"農曆",
	"Sunrise":"日出",
	"Sunset":"日落",
	"Moonrise":"月出",
	"Moonset":"月落",
	"Tide":"潮汐",
	"Tide time":"潮汐時間",
	"Height":"高度"
}


def print_info(translate=False, root=None):
	if not root:
		root = info
	for k in root.keys():
		v = root[k]
		if translate and k in translation:
			k = translation[k]
		print(k + ": " + v)

def print_array(info, translate=True):
	for d in info:
		print()
		print_info(translate, d)

def print_help():
	print("Usage: hko_report <options>")
	print("  options")
	print("     -l, --lastest          show lastest general weather information")
	print("     -9, --9days            show 9 days weather forcast")
	print("     -a, --astron           show astronomical observation")
	print("     --all                  show all information")
	print("     --english              show information in English")

def main():
	translate = True
	args = sys.argv[1:]
	if len(args) > 0:
		if "--english" in args:
			translate = False
			global api_url
			api_url = api_url_eng
		json_s = urlopen(api_url, timeout=6).read().decode("utf8")
		json_dict = json.loads(json_s, encoding="utf8")
		set_json_data(json_dict)
		if "--lastest" in args or "-l" in args or "--all" in args:
			build_dict(info_map, info)
			print_info(translate)
		if "-a" in args or "--astron" in args or "--all" in args:
			print()
			build_dict(astron_info_map, astron_info)
			print_info(translate, astron_info)
			build_array(tide_info_map, tide_info)
			print_array(tide_info, translate)
		if "--9days" in args or "-9" in args or "--all" in args:
			build_array(nine_day_map, nine_day_info)
			print_array(nine_day_info, translate)
	else:
		print_help()

if __name__ == "__main__":
	main()
