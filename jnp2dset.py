#!/usr/bin/python3

import re
import copy



ocbracket = '{'
ccbracket = '}'
obracket = '['
cbracket = ']'
scolon = ';'

DEBUG = 0

def pdebug(msg, level):
    if DEBUG > level:
        print("+++[D{}]: {}".format(level, msg))


class DsetConvert():

    def __init__(self, config):

        self.conf = copy.deepcopy(config)
        self.dset = { "set": []}



    def convert(self):
        lst = []
        while len(self.conf):
            pdebug(self.conf[0], 11)
            match = re.search("(.+?);", self.conf[0])
            if match:
                pdebug(" [;] : {}".format(self.conf[0]), 5)
                lst.append(match.group(1))
                self._pop()
                continue
            match = re.search("(.+?) {", self.conf[0])
            if match:
                pdebug(" [cbracket open] : {}".format(self.conf[0]), 5)
                self._pop()
                key = match.group(1)
                lst.append({ key: self.convert()})
                continue
            match = re.search("(.+?) \[ (.+?) \];", self.conf[0])
            if match:
                pdebug(" [[]] : {}".format(self.conf[0]), 5)
                self._pop()
                key = match.group(1)
                values = match.group(2).split(" ")
                lst.append({ key: values})
                continue
            match = re.search("}", self.conf[0])
            if match:
                pdebug(" [cbracket close] : {}".format(self.conf[0]), 5)
                self._pop()
                return lst
            match = re.search("^#", self.conf[0])
            if match:
                pdebug(" [#] : {}".format(self.conf[0]), 5)
                self._pop()
                continue
        return lst



    def _pop(self):
        self.conf = self.conf[1:]


    def print_dset(self):
        for key in self.dset:
            print(key)
            print(self.dset[key])
            for i in range(len(self.dset[key])):
                print(self.dset[key][i])


    def translate(self):
        self.dset["set"] = self.convert()
        print(self.dset)



    def print_prefix(self, prefix, lst):
        for i in range(len(lst)):
            if type(lst[i]) is dict:
                for key in lst[i]:
                    self.print_prefix("{} {}".format(prefix, key), lst[i][key])
            else:
                print("{} {}".format(prefix, lst[i]))











def main():
    with open("R8.cfg", "r") as fd:
        config = fd.readlines()
    for i in range(len(config)):
        config[i] = config[i].rstrip().lstrip()
        print(config[i])
    dset = DsetConvert(config)
    dset.translate()
    dset.print_prefix("set", dset.dset["set"])
    #dset.translate()












if __name__ == "__main__":
    main()

