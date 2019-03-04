import os
import re

base_path = ""
old_name2new_name_map = dict()
for each in os.listdir(base_path):
    new_file_name = "意难忘_" + re.search("\d+", each).group(1) + ".flv"
    old_name2new_name_map[each] = new_file_name

for k, v in old_name2new_name_map.items():
    print(k, v)

