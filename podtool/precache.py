#!/usr/bin/env python

import os
from distutils.version import LooseVersion
import json
import glob


download_cache_directory = '/Users/everettjf/cache_supotato'

class Command:
    def __init__(self):
        self.cmds = []

    def add(self, cmd):
        self.cmds.append(cmd)

    def run(self):
        s = ' ; '.join(self.cmds)
        print(s)
        os.system(s)


def download_git(podname, git, tag=None, commit=None):
    """
        git clone
    for tag:
        git checkout tags/xxxx
    for commit:
        git checkout yyyyyy
    :param podname:
    :param git:
    :param tag:
    :param commit:
    :return:
    """
    path = os.path.join(download_cache_directory, podname)

    if os.path.exists(path):
        return path

    cmd = Command()
    cmd.add('cd ' + download_cache_directory)
    cmd.add('git clone ' + git + ' ' + podname)

    cmd.add('cd ' + path)
    if tag is not None:
        cmd.add('git checkout tags/' + tag)
    elif commit is not None:
        cmd.add('git checkout ' + commit)

    cmd.run()

    return path


def download_http(podname, http):
    # wget xxxxxxxx -O name
    # cmd('cd ' + download_cache_directory)
    # cmd('wget ' + http + ' -O ' + podname)
    # unzip
    # ignore
    pass


def download_source(podname, source):
    # 4 types:
    # - git
    # - git tag
    # - git commit
    # - http (zip)

    source_dir = None

    if 'git' in source:
        if 'tag' in source:
            # git & tag
            # print(source)
            source_dir = download_git(podname,source['git'], tag=source['tag'])
        elif 'commit' in source:
            # git & commit
            source_dir = download_git(podname,source['git'], commit=source['commit'])
        else:
            # git
            source_dir = download_git(podname,source['git'])

    elif 'http' in source:
        # print(source)
        # download_http(podname, source['http'])
        # ignore
        pass
    else:
        # svn hg
        # print(source)
        # ignore
        pass

    return source_dir


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
        print('-----------')
        print(source_dir)
        print(source_files)
        print(type(source_files))
        print(': after glob =')

        if isinstance(source_files, list):
            for source_file in source_files:
                files = glob.glob(os.path.join(source_dir, source_file))
                print(files)
        elif isinstance(source_files, str):
            source_file = source_files
            files = glob.glob(os.path.join(source_dir, source_file))
            print(files)
        else:
            print(source_files)
            pass

    if public_header_files is not None:
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
    with open(podspec_filepath) as json_file:
        podspec = json.load(json_file)

        source = podspec['source']
        if source is None:
            return
        # download the source
        source_dir = download_source(podname, source)
        if source_dir is None:
            return

        check_files(podname, source_dir, podspec)

        if 'subspecs' in podspec:
            for subspec in podspec['subspecs']:
                check_files(podname, source_dir, subspec, sub=True)


def fetch_latest_version(podpath):
    versions = os.listdir(podpath)
    if len(versions) == 0:
        return None

    loose_versions = [LooseVersion(ver) for ver in versions]
    return str(max(loose_versions))


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

    cnt = 0
    for podname in pods:
        cnt += 1
        if cnt > 10:
            break

        # filter some podname
        if len(podname) <= 2:
            continue
        if not podname[:1].isalpha() and not podname[:1].isdigit():
            continue

        podpath = os.path.join(spec_base, podname)

        build_pod(podname, podpath)


if __name__ == '__main__':

    spec_base = '/Users/everettjf/Downloads/Specs-master/Specs'
    build(spec_base)
