#!/usr/bin/python3
'''
Author:    Miguel Gonzalez
Version:   1.0
Date:      20/11/2016
'''


import re
import sys
import getopt
import logging
logger = logging.getLogger(__name__)


DEBUG = 0


def pdebug(msg, level):
    if DEBUG > level:
        print("+++[D{}]: {}".format(level, msg))


class DsetConvert():
    ''' Class used to translate a configuration to display set format.
It converts configuration to a python data structure based of lists and dictionaries.
Then it prints the configuration in display set format 
    '''

    def __init__(self, config=None):
        ''' Initialize class with the config file. If no config file is provided it reads from stdin'''

        if config:
            try:
                with open(config, "r") as fd:
                    self.conf = fd.readlines()
            except:
                print("Error: file {} does not exists".format(config))
                sys.exit(0)
        else:
            try:
                self.conf = sys.stdin.readlines()
            except:
                print("error reading from standard input")

        for i in range(len(self.conf)):
            self.conf[i] = self.conf[i].rstrip().lstrip()

        self.dset = {"set": []}

    def convert(self):
        ''' recurrent method to translate configuration to python data structure'''
        lst = []
        while len(self.conf):
            logger.debug(self.conf[0])
            # detect comments and ignore them
            match = re.search("^#", self.conf[0])
            if match:
                logger.debug(" [#] : {}".format(self.conf[0]))
                self._pop()
                continue
            # Ignore comments
            match = re.search("^/\*", self.conf[0])
            if match:
                self._pop()
                continue
            # Detect statements with brackets []
            match = re.search("(.+?) \[ (.+?) \];", self.conf[0])
            if match:
                logger.debug(" [[]] : {}".format(self.conf[0]))
                self._pop()
                key = match.group(1)
                values = match.group(2).split(" ")
                lst.append({key: values})
                continue
            # detect final statements that do not have nested stanzas
            match = re.search("(.+?);( ## SECRET-DATA){0,1}$", self.conf[0])
            if match:
                logger.debug(" [;] : {}".format(self.conf[0]))
                lst.append(match.group(1))
                self._pop()
                continue
            # detect a new stanza
            match = re.search("(.+?) {", self.conf[0])
            if match:
                logger.debug(" [cbracket open] : {}".format(self.conf[0]))
                self._pop()
                key = match.group(1)
                lst.append({key: self.convert()})
                continue
            # detect the end of a stanza
            match = re.search("}", self.conf[0])
            if match:
                logger.debug(" [cbracket close] : {}".format(self.conf[0]))
                self._pop()
                return lst
            #If the scripts reaches this point line has not matches against any rule
            #so there is an error. Print line with problem and skip it
            print("################################################")
            print("### ERROR line: {}".format(self.conf[0]))
            print("### Skip line and continue")
            print("################################################")
            self._pop()
            logger.debug("ERROR")
        return lst

    def _pop(self):
        '''Pop first line of the current configuration'''
        self.conf = self.conf[1:]

    def translate(self):
        '''Invoke convert method to translate configuration'''
        self.dset["set"] = self.convert()
        # print(self.dset)

    def print_prefix(self, prefix, lst):
        '''Recurrent method used to print configuration in display set format'''
        for i in range(len(lst)):
            if type(lst[i]) is dict:
                for key in lst[i]:
                    self.print_prefix("{} {}".format(prefix, key), lst[i][key])
                    match = re.search("inactive: ", key)
                    if match:
                        line = "{} {}".format(
                            prefix, key).replace("inactive: ", "")
                        line = re.sub(r"^set", "deactivate", line)
                        print(line)
            else:
                match = re.search("inactive: ", lst[i])
                if match:
                    line = "{} {}".format(prefix, lst[i]).replace("inactive: ", "")
                    # print line in set format
                    print(line)
                    line = re.sub(r"^set", "deactivate", line)
                    # deactivate previous line
                    print(line)
                else:
                    print("{} {}".format(prefix, lst[i]).replace("inactive: ", ""))


def _info():
    print("""Usage: jnp2dset.py -i <config-file>
                    jnp2dset.py: enter configuration and then ctrl+d or pipe configuration
                                 to jnp2set""")

def main(argv):

    try:
        opts, args = getopt.getopt(argv, "hi:v", ["input-config"])
    except getopt.GetoptError:
        _info()
        sys.exist(2)
    debug_level = logging.INFO
    for opt, arg in opts:
        if opt == '-h':
            _info()
            sys.exit(0)
        elif opt in ("-i", "--input-config"):
            dset = DsetConvert(config=arg)
        elif opt == '-v':
            debug_level = logging.DEBUG


    logging.basicConfig(level=debug_level,
                        format='%(asctime)s '
                            '%(filename)s: '    
                            '%(levelname)s: '
                            '%(funcName)s(): '
                            '%(lineno)d:\t'
                            '%(message)s')
    #read from stdin
    if not len(opts):
        dset = DsetConvert()

    dset.translate()
    dset.print_prefix("set", dset.dset["set"])


if __name__ == "__main__":
    main(sys.argv[1:])
