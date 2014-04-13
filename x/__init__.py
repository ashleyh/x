#!/usr/bin/env python

from __future__ import print_function

import sys
import subprocess
import os
import argparse
import tempfile
import errno
import collections
import requests
import re
from autowire import autowire


def tar(path, work_dir):
    subprocess.call(['tar', '-x', '-C', work_dir, '-f', path])


def tar_bz2(path, work_dir):
    subprocess.call(['tar', '-x', '-j', '-C', work_dir, '-f', path])


def tar_gz(path, work_dir):
    subprocess.call(['tar', '-x', '-z', '-C', work_dir, '-f', path])


Info = collections.namedtuple('Info', 'extractor basename')


# XXX terrible name
def guess_info(path):
    formats = [
        ('tar', tar),
        ('tar.bz2', tar_bz2),
        ('tar.gz', tar_gz),
    ]
    for ext, cmd in formats:
        dot_ext = '.' + ext
        if path.endswith(dot_ext):
            return Info(
                extractor=cmd,
                basename=os.path.basename(path)[:-len(dot_ext)],
            )
    return None


def get_only_child(path):
    children = os.listdir(path)
    if len(children) == 1:
        return children[0]
    else:
        return None


def rename(src, dest):
    n = 0
    while True:
        try:
            dest_ = dest if n == 0 else '{}-{}'.format(dest, n)
            os.rename(src, dest_)
        except OSError as e:
            if e.errno == errno.ENOTEMPTY:
                n += 1
                continue
            else:
                raise e
        except e:
            raise e
        else:
            break


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')


def longest_extension(url):
    m = re.search(r'\.[^/]+$', url)
    if m:
        return m.group(0)
    else:
        return ''


def download(url):
    f = tempfile.NamedTemporaryFile(suffix=longest_extension(url), delete=False)
    r = requests.get(url)
    r.raise_for_status()
    for block in r.iter_content(chunk_size=1024):
        f.write(block)
    f.close()
    return f.name


def maybe_download(path_or_url):
    if is_url(path_or_url):
        path = download(path_or_url)
        target_dir = '.'
    else:
        path = path_or_url
        target_dir = os.path.dirname(path)
    return {
        'path': path,
        'target_dir': target_dir,
    }


class CouldntGuess(Exception): pass


def find_extractor(path):
    info = guess_info(path)
    if info is None:
        raise CouldntGuess()
    return {
        'extractor': info.extractor,
        'basename': info.basename,
    }


def make_work_dir(target_dir):
    work_dir = tempfile.mkdtemp(dir=target_dir)
    return {'work_dir': work_dir}


def run_extractor(extractor, path, work_dir):
    extractor(path=path, work_dir=work_dir)
    return {}


def squash_dirs(work_dir, basename, target_dir):
    only_child = get_only_child(work_dir)
    if only_child is None:
        rename(work_dir, os.path.join(target_dir, basename))
    else:
        rename(
            os.path.join(work_dir, only_child),
            os.path.join(target_dir, only_child)
        )
        os.rmdir(work_dir)
    return {}


def act(args):
    state = {
        'path_or_url': args.path,
    }
    bits = [maybe_download, find_extractor, make_work_dir, run_extractor, squash_dirs]
    try:
        autowire(state, bits)
    except CouldntGuess:
        print("Couldn't guess type")
        return 1
    else:
        return 0


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args(argv)
    return act(args)


def entry_point():
    sys.exit(main(sys.argv[1:]))
