import sys
import json
import datetime
from collections import OrderedDict
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs


api_url = "http://www.hko.gov.hk/wxinfo/json/one_json_uc.xml"
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
	"Weather":"天氣"
}
d = None

def iter_anything2str(e):
	s = ""
	if type(e) is str:
		return e
	if isinstance(e, dict):
		for k in e.keys():
			s += k + ": " + iter_anything2str(e[k]) + "\n"
	if isinstance(e, list):
		for ele in e:
			s += iter_anything2str(ele) + "\n"
	return s

def get_value(levels, str_only=True, root=None):
	null_value = ["//", ""]
	levels = levels.split("/")

	if root:
		e = root
	else:
		e = d

	for l in levels:
		if l not in e:
			return "N/A"
		e = e[l]

	if e is None or e in null_value:
		return "N/A"
	
	if str_only:
		e = iter_anything2str(e)
		# try parse html
		soup = bs(e, "html.parser").findAll(text=True)
		return "".join(soup)
	else:
		return e

def build_info():
	for k in info_map.keys():
		v = info_map[k]
		s = ""
		if type(v) is tuple:
			for t in v:
				if len(t) > 5 and t[0:5] == "+str:":
					s += t[5:]
				else:
					s += get_value(t)
		else:
			s += get_value(v)
		info[k] = s

def build_9D():
	forcasts = get_value(nine_day_map["root"], str_only=False)
	for f in forcasts:
		day = OrderedDict()
		for k in nine_day_map.keys():
			if k != "root":
				v = nine_day_map[k]
				s = ""
				if type(v) is tuple:
					for t in v:
						if len(t) > 5 and t[0:5] == "+str:":
							s += t[5:]
						else:
							s += get_value(t, root=f)
				else:
					s += get_value(v, root=f)
				if k == "Date":
					s = str(datetime.datetime.strptime(s, "%Y%m%d").date())
				day[k] = s
		nine_day_info.append(day)


def print_info(translate=False, root=None):
	if not root:
		root = info
	for k in root.keys():
		v = root[k]
		if translate and k in translation:
			k = translation[k]
		print(k + ": " + v)

def print_9D():
	for d in nine_day_info:
		print()
		print_info(True, d)

def print_help():
	print("Usage: hko_report <options>")
	print("  options")
	print("     -l, --lastest          show lastest general weather information")
	print("     -9, --9days            show 9 days weather forcast")
	print("     --all                  show all information")

def main():
	global d
	args = sys.argv[1:]
	if len(args) > 0:
		json_s = urlopen(api_url, timeout=6).read().decode("utf8")
		d = json.loads(json_s, encoding="utf8")
		if "--lastest" in args or "-l" in args or "--all" in args:
			build_info()
			print_info(translate=True)
		if "--9days" in args or "-9" in args or "--all" in args:
			build_9D()
			print_9D()
	else:
		print_help()

if __name__ == "__main__":
	main()
