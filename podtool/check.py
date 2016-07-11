#!/usr/bin/env python

import sqlite3


class Check:
    def __init__(self):
        self.conn = sqlite3.connect('/Users/everettjf/GitHub/supotato/db/supotato.db')
        self.mapper = {}

    def load(self):
        cursor = self.conn.execute('select filename,podname from filemap')
        for row in cursor:
            self.mapper[row[0]] = row[1]

    def check(self, filename):
        if filename in self.mapper:
            return self.mapper[filename]
        return None



def test():
    c = Check()
    c.load()

    print('check %s' % c.check('AFNetworking.h'))

if __name__ == '__main__':
    test()


