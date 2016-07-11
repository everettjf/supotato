#!/usr/bin/env python

import sqlite3
import os


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

    pods = {}
    input = '/Users/everettjf/z/f/headers/'
    for root, dirs, files in os.walk(input):
        for f in files:
            if not f.endswith('.h'):
                continue

            path = os.path.join(root, f)
            filename = os.path.relpath(path, input)

            podname = c.check(filename)
            if podname is not None:
                pods[podname] = 1

    for pod in pods:
        print(pod)


if __name__ == '__main__':
    test()


