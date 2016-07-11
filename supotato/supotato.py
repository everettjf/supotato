#!/usr/bin/env python
import argparse
import os
import six
import sys
from six.moves import getcwd
import sqlite3


# global checker
checker = None


class Check:
    def __init__(self):
        dbpath = '/var/tmp/supotato/supotato.db'
        if os.path.exists(dbpath):
            self.conn = sqlite3.connect(dbpath)
        self.mapper = {}

    def load(self):
        if self.conn is None:
            return

        cursor = self.conn.execute('select filename,podname from filemap')
        for row in cursor:
            self.mapper[row[0]] = row[1]

    def check(self, filename):
        if filename in self.mapper:
            return self.mapper[filename]
        return None

    def fetch_cocoapods_link_and_info(self, podname):
        if self.conn is None:
            return '',''

        cursor = self.conn.execute("select podname,podlink,podinfo from cocoapods where podname = '" + podname + "'")
        for row in cursor:
            return row[1],row[2]
        return '',''


def moveto(file, from_folder, to_folder):
    from_file = os.path.join(from_folder, file)
    to_file = os.path.join(to_folder, file)

    # to move only files, not folders
    if os.path.isfile(from_file):
        if not os.path.exists(to_folder):
            os.makedirs(to_folder)
        os.rename(from_file, to_file)


def _format_text_arg(arg):
    if not isinstance(arg, six.text_type):
        arg = arg.decode('utf-8')
    return arg


def _format_arg(arg):
    if isinstance(arg, six.string_types):
        arg = _format_text_arg(arg)
    return arg


def classify(input=None, output=None, sortby="prefix", asc=True, prefix_length=2):
    """
    classify .h files
    :param input: directory that .h files in
    :param output: directory for the txt file
    :param sort: prefix=sort by prefix ; count=sort by file count ; other default to prefix
    :param desc: True, otherwize asc
    :param prefix_length: default 2
    :return:
    """

    if input is None:
        input = getcwd()

    sortindex = 0
    if sortby == "count":
        sortindex = 1

    print('Start analyzing directory:' + input)

    cocoapods = {}
    podsdummys = []
    mapper = {}

    for root, dirs, files in os.walk(input):
        for f in files:
            if not f.endswith('.h'):
                continue

            path = os.path.join(root, f)
            filename = os.path.relpath(path, input)

            prefix = f[:prefix_length]

            # mapper
            if prefix in mapper:
                mapper[prefix].append(filename)
            else:
                mapper[prefix] = [filename]

            # pod dummy
            if filename.startswith('PodsDummy'):
                podsdummys.append(filename)

            # cocoapods
            podname = checker.check(filename)
            if podname is not None:
                cocoapods[podname] = 1

    counter = {}
    for prefix in mapper:
        files = mapper[prefix]
        counter[prefix] = len(files)

    if six.PY2:
        ordered = sorted(counter.iteritems(), key=lambda d:d[sortindex], reverse=not asc)
    else:
        ordered = sorted(counter.items(), key=lambda d:d[sortindex], reverse=not asc)

    # console output ######################################
    # - cocoa pods
    if len(cocoapods.keys()) > 0:
        print('CocoaPods (%d) : ' % len(cocoapods.keys()))
        for pod in cocoapods:
            print('    ' + pod)

            link, info = checker.fetch_cocoapods_link_and_info(pod)
            print('        ' + link)
            print('        ' + info)

    # - pods dummy
    if len(podsdummys) > 0:
        print('Pods Dummy Files (%d):' % len(podsdummys))
    for pod in podsdummys:
        print('    ' + pod)

    # - file mapper
    total_file_count = 0
    for tuple in ordered:
        prefix = tuple[0]
        files = mapper[prefix]

        print("%s  (%d)" %(prefix, len(files)))

        total_file_count += len(files)

        for file in files:
            print("    " + file)

    if total_file_count == 0:
        print('No header (.h) files found , please specify target directory with -i option.')
        print('Or try --help for more options.')
    else:
        print("--- Total %d files ---"% total_file_count)

    # file output ########################################
    if output is not None:
        if os.path.isdir(output):
            output = os.path.join(output, "result.txt")

        if os.path.isfile(output):
            print('!!!! output file already exist : %s !!!!' % output)
            return

        with open(output,mode='a+') as f:
            # - CocoaPods
            if len(cocoapods.keys()) > 0:
                f.write('CocoaPods (%d) : \n' % len(cocoapods.keys()))
                for pod in cocoapods:
                    f.write('    ' + pod + '\n')
                    link, info = checker.fetch_cocoapods_link_and_info(pod)
                    f.write('        ' + link + '\n')
                    f.write('        ' + info + '\n')

            # - pods dummy
            if len(podsdummys) > 0:
                f.write('Pods Dummy Files (%d):\n' % len(podsdummys))
            for pod in podsdummys:
                f.write('    ' + pod + '\n')

            f.write('\n')

            for tuple in ordered:
                prefix = tuple[0]
                files = mapper[prefix]

                f.write("%s  (%d)\n" %(prefix, len(files)))

                for file in files:
                    if six.PY2:
                        line = file.encode('utf-8')
                    else:
                        line = file
                    f.write("    " + line + "\n")
            f.write("--- Total %d files ---"% total_file_count)

    print('Finish analyzing directory:' + input)


def _get_param(value, default):
    if value is None:
        return default
    return _format_arg(value)


def check_cocoapods_db():
    dbdir = '/var/tmp/supotato'
    dbpath = '/var/tmp/supotato/supotato.db'
    if os.path.exists(dbpath):
        return

    if not os.path.exists(dbdir):
        os.mkdir(dbdir)

    import urllib.request
    url = "https://everettjf.github.io/app/supotato/supotato.db"

    print('CocoaPods Index Database not exist , will download from ' + url)
    print('Please wait for a moment (about 5 MB file will be downloaded)')

    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(dbpath, 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)

    print('Download completed')


def force_update_db():
    dbdir = '/var/tmp/supotato'
    dbpath = '/var/tmp/supotato/supotato.db'
    if os.path.exists(dbpath):
        os.remove(dbpath)

    if not os.path.exists(dbdir):
        os.mkdir(dbdir)

    import urllib.request
    url = "https://everettjf.github.io/app/supotato/supotato.db"

    print('CocoaPods Index Database not exist , will download from ' + url)
    print('Please wait for a moment (about 5 MB file will be downloaded)')

    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(dbpath, 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)

    print('Download completed')
    print('Update succeed')


def main():
    description = "Generate a simple report for header files in your directory"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-i", "--input", type=str, help="directory that header(.h) files in. ")
    parser.add_argument("-o", "--output", type=str, help="file (or directory) path to put txt report in.")
    parser.add_argument("-s", "--sortby", type=str, help="prefix or count . Means sort by prefix or count.")
    parser.add_argument("-d", "--order", type=str, help="desc or asc.")
    parser.add_argument("-p", "--prefixlength", type=int, help="prefix length for classify , default to 2.")
    parser.add_argument("-u", "--updatedb", help="force update cocoapods database.")

    args = parser.parse_args()

    output = _get_param(args.output, None)
    input = _get_param(args.input, getcwd())
    sortby = _get_param(args.sortby, "prefix")
    is_asc = _get_param(args.order, "asc") == "asc"
    prefixlength = int(_get_param(args.prefixlength, "2"))

    forceupdate = args.updatedb
    if forceupdate is not None:
        force_update_db()
        sys.exit()

    check_cocoapods_db()

    global checker
    checker = Check()
    checker.load()

    classify(input, output, sortby=sortby, asc=is_asc, prefix_length=prefixlength)

    sys.exit()


if __name__ == '__main__':
    main()
