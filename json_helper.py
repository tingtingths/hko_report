import json
import datetime
from collections import OrderedDict
from bs4 import BeautifulSoup as bs


class JsonHelper:
    def __init__(self, data):
        self.json_data = data

    def iter_anything2str(self, e):
        s = ""
        if type(e) is str:
            return e
        if isinstance(e, dict):
            for k in e.keys():
                s += k + ": " + self.iter_anything2str(e[k]) + "\n"
        if isinstance(e, list):
            for ele in e:
                s += self.iter_anything2str(ele) + "\n"
        return s

    def get_value(self, levels, str_only=True, root=None):
        null_value = ["//", ""]
        levels = levels.split("/")

        if root:
            e = root
        else:
            e = self.json_data

        for l in levels:
            if l not in e:
                return "N/A"
            e = e[l]

        if e is None or e in null_value:
            return "N/A"

        if str_only:
            e = self.iter_anything2str(e)
            # try parse html
            soup = bs(e, "html.parser").findAll(text=True)
            return "".join(soup)
        else:
            return e

    def build_dict(self, root):
        d = OrderedDict()
        for k in root.keys():
            v = root[k]
            s = ""
            if type(v) is tuple:
                for t in v:
                    if len(t) > 5 and t[0:5] == "+str:":
                            s += t[5:]
                    else:
                        s += self.get_value(t)
            else:
                s += self.get_value(v)
            d[k] = s
        return d

    def build_array(self, root):
        a = []
        forcasts = self.get_value(root["root"], str_only=False)
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
                                s += self.get_value(t, root=f)
                    else:
                        s += self.get_value(v, root=f)
                    if k == "Date":
                        s = str(datetime.datetime.strptime(s, "%Y%m%d").date())
                    day[k] = s
            a.append(day)
        return a
