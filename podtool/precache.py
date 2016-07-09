#!/usr/bin/env python

import os
from distutils.version import LooseVersion
import json


def parse_podspec(podspec_filepath):
    with open(podspec_filepath) as json_file:
        podspec = json.load(json_file)

        source = podspec['source']
        # print(source)

        # 4 types:
        # - git
        # - git tag
        # - git commit
        # - http (zip)

        if 'git' in source:
            if 'tag' in source:
                # git & tag
                pass
            elif 'commit' in source:
                # git & commit
                pass
            else:
                # git
                pass
        elif 'http' in source:
            pass
        else:
            #unknown

            print(source)



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
    # print(podname)
    # print(versionpath)

    podspec_jsonpath = os.path.join(versionpath, podname + '.podspec.json')
    # print(podspec_jsonpath)

    parse_podspec(podspec_jsonpath)



def build(spec_base):
    pods = os.listdir(spec_base)

    for podname in pods:
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
