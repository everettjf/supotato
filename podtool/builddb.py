#!/usr/bin/env python
"""
1. make the relation between .h files and cocoapods name
2. write all the pod info into local sqlite db
"""

import os
from distutils.version import LooseVersion
import json
import glob
import re
import sqlite3


download_cache_directory = '/Users/everettjf/cache_supotato'

conn = None


def db_init_table():
    conn.execute('''
    create table cocoapods
    (
    podname char(50) primary key not null,
    podlink text,
    podinfo text
    );
    ''')

    conn.execute('''
    create table filemap
    (
    filename char(100) primary key not null,
    podname char(50) not null
    );
    ''')


def db_add_header(filename, podname):
    print('--------------')
    print(podname)
    print(filename)

    conn.execute("replace into filemap values(?,?)",
                 (filename, podname))


def db_add_pod(podname, podlink, podinfo):
    print('************')
    print(podname)
    print(podlink)
    print(podinfo)
    conn.execute("replace into cocoapods values(?,?,?)",
                 (podname, podlink, podinfo))






def parse_headers(podname, source_dir, pattern):
    # replace .{h,m} pattern to .h pattern
    # because python glob can not support ruby pathname style glob
    pattern = re.sub(r'\.\{\S+\}', '.h',pattern)

    files = glob.glob(os.path.join(source_dir, pattern))

    if len(files) == 0:
        return

    for filepath in files:
        filename = os.path.split(filepath)[-1]
        fileext = os.path.splitext(filename)[1]

        if fileext != '.h':
            continue

        db_add_header(filename, podname)


def check_files(podname, source_dir, podspec , sub=False):
    source_files = None
    if 'source_files' in podspec:
        source_files = podspec['source_files']

    public_header_files = None
    if 'public_header_files' in podspec:
        public_header_files = podspec['public_header_files']

    if source_files is None and public_header_files is None:
        # print(podspec)
        return

    if source_files is not None:
        # print('-----------')
        # print(source_dir)
        # print(source_files)
        # print(type(source_files))
        # print(': after glob =')

        if isinstance(source_files, list):
            for source_file in source_files:
                parse_headers(podname, source_dir, source_file)
        elif isinstance(source_files, str):
            source_file = source_files
            parse_headers(podname, source_dir, source_file)
        else:
            print(source_files)
            pass

    if public_header_files is not None:
        if isinstance(public_header_files, list):
            for pattern in public_header_files:
                parse_headers(podname, source_dir, pattern)
        elif isinstance(public_header_files, str):
            pattern = public_header_files
            parse_headers(podname, source_dir, pattern)
        else:
            # print(public_header_files)
            pass


def parse_podspec(podname,podspec_filepath):
    """
    clone the repo

    get header file names (*.h)


    :param podname:
    :param podspec_filepath:
    :return:
    """
    with open(podspec_filepath,encoding='utf-8') as json_file:
        podspec = json.load(json_file)

        source = podspec['source']
        if source is None:
            return
        # download the source

        source_dir = os.path.join(download_cache_directory, podname)

        check_files(podname, source_dir, podspec)

        if 'subspecs' in podspec:
            for subspec in podspec['subspecs']:
                check_files(podname, source_dir, subspec, sub=True)

        summary = ''
        if 'summary' in podspec:
            summary = podspec['summary']

        homepage = ''
        if 'homepage' in podspec:
            homepage = podspec['homepage']

        db_add_pod(podname, homepage, summary)


def fetch_latest_version(podpath):
    try:
        versions = os.listdir(podpath)
        if len(versions) == 0:
            return None

        loose_versions = [LooseVersion(str(ver)) for ver in versions]
        return str(max(loose_versions))
    except:
        pass
    return None


def build_pod(podname, podpath):
    latest_version = fetch_latest_version(podpath)
    if latest_version is None:
        print('can not locate latest version for : %s' % podpath)
        return

    versionpath = os.path.join(podpath, latest_version)

    podspec_jsonpath = os.path.join(versionpath, podname + '.podspec.json')

    parse_podspec(podname, podspec_jsonpath)


def build(spec_base):
    pods = os.listdir(spec_base)

    for podname in pods:
        podname = podname.replace('(', '')
        podname = podname.replace(')', '')

        # filter some podname
        if len(podname) <= 2:
            continue
        if not podname[:1].isalpha() and not podname[:1].isdigit():
            continue

        podpath = os.path.join(spec_base, podname)

        build_pod(podname, podpath)


if __name__ == '__main__':

    conn = sqlite3.connect('/Users/everettjf/supotato.db')
    # db_init_table()

    spec_base = '/Users/everettjf/Downloads/Specs-master/Specs'

    build(spec_base)

    conn.commit()

