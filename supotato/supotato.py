#!/usr/bin/env python
import argparse
import os
import six
import sys

from six.moves import getcwd


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

    mapper = {}
    for root, dirs, files in os.walk(input):
        for f in files:
            if not f.endswith('.h'):
                continue

            path = os.path.join(root, f)
            path = os.path.relpath(path, input)

            prefix = f[:prefix_length]

            if prefix in mapper:
                mapper[prefix].append(path)
            else:
                mapper[prefix] = [path]

    counter = {}
    for prefix in mapper:
        files = mapper[prefix]
        counter[prefix] = len(files)

    if six.PY2:
        ordered = sorted(counter.iteritems(), key=lambda d:d[sortindex], reverse=not asc)
    else:
        ordered = sorted(counter.items(), key=lambda d:d[sortindex], reverse=not asc)


    # console output
    total_file_count = 0
    for tuple in ordered:
        prefix = tuple[0]
        files = mapper[prefix]

        print("%s  (%d)" %(prefix, len(files)))

        total_file_count += len(files)

        for file in files:
            print("    " + file)

    print("--- Total %d files ---"% total_file_count)

    # file output
    if output is not None:
        if os.path.isdir(output):
            output = os.path.join(output, "result.txt")

        if os.path.isfile(output):
            print('!!!! output file already exist : %s !!!!' % output)
            return

        with open(output,mode='a+') as f:
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


def _get_param(value, default):
    if value is None:
        return default
    return _format_arg(value)


def main():
    description = "Generate a simple report for header files in your directory"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-i", "--input", type=str, help="directory that header(.h) files in. ")
    parser.add_argument("-o", "--output", type=str, help="file (or directory) path to put txt report in.")
    parser.add_argument("-s", "--sortby", type=str, help="prefix or count . Means sort by prefix or count.")
    parser.add_argument("-d", "--order", type=str, help="desc or asc.")
    parser.add_argument("-p", "--prefixlength", type=int, help="prefix length for classify , default to 2.")

    args = parser.parse_args()

    output = _get_param(args.output, getcwd())
    input = _get_param(args.input, getcwd())
    sortby = _get_param(args.sortby, "prefix")
    is_asc = _get_param(args.order, "asc") == "asc"
    prefixlength = int(_get_param(args.prefixlength, "2"))

    classify(input, output, sortby=sortby, asc=is_asc, prefix_length=prefixlength)

    sys.exit()


if __name__ == '__main__':
    main()
