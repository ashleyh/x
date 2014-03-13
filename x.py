#!/usr/bin/env python

from __future__ import print_function

import sys
import subprocess
import os
import argparse
import tempfile


def tar(path, work_dir):
    subprocess.call(['tar', '-x', '-C', work_dir, '-f', path])


# XXX terrible name
def guess_info(path):
    formats = [
        ('tar', tar),
    ]
    for ext, cmd in formats:
        dot_ext = '.' + ext
        if path.endswith(dot_ext):
            return path[:-len(dot_ext)], cmd
    return None


def get_only_child(path):
    children = os.listdir(path)
    if len(children) == 1:
        return children[0]
    else:
        return None


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args(argv)
    dirname, basename = os.path.split(args.path)
    info = guess_info(args.path)
    if info is None:
        print("Couldn't guess type of", args.path, file=sys.stderr)
        return 1
    expanded_path, cmd = info
    work_dir = tempfile.mkdtemp(prefix=basename, dir=dirname)
    cmd(path=args.path, work_dir=work_dir)
    only_child = get_only_child(work_dir)
    if only_child is None:
        os.rename(work_dir, expanded_path)
    else:
        os.rename(
            os.path.join(work_dir, only_child),
            os.path.join(dirname, only_child)
        )
        os.rmdir(work_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
