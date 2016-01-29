import json
import datetime
from collections import OrderedDict
from bs4 import BeautifulSoup as bs


json_data = None

def set_json_data(data):
	global json_data
	json_data = data

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
		global json_data
		e = json_data

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

def build_dict(root, info):
	for k in root.keys():
		v = root[k]
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

def build_array(root, info):
	forcasts = get_value(root["root"], str_only=False)
	for f in forcasts:
		day = OrderedDict()
		for k in root.keys():
			if k != "root":
				v = root[k]
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
		info.append(day)
