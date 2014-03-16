import py.path
from x import main


test_dir = py.path.local('test')


def paths(dir):
    return set(child.relto(dir) for child in dir.visit())


def test_does_nothing_to_unknown_file(tmpdir):
    tmpdir.chdir()
    tmpdir.join('foo').write('bar')
    assert main(['foo']) == 1
    assert paths(tmpdir) == set(['foo'])


def extract_test(tmpdir, archive, files):
    tmpdir.chdir()
    test_dir.join(archive).copy(tmpdir.join(archive))
    assert main([archive]) == 0
    assert paths(tmpdir) == set(files + [archive])


def test_untars_rooted(tmpdir):
    extract_test(tmpdir, 'rooted.tar',
                 ['root', 'root/a', 'root/b'])


def test_untars_rooted_with_conflict(tmpdir):
    tmpdir.mkdir('root')
    tmpdir.join('root', 'foo').write('bar')
    extract_test(tmpdir, 'rooted.tar',
                 ['root', 'root/foo', 'root-1', 'root-1/a', 'root-1/b'])


def test_untars_unrooted(tmpdir):
    extract_test(tmpdir, 'unrooted.tar',
                 ['unrooted', 'unrooted/a', 'unrooted/b'])


def test_untars_unrooted_conflict(tmpdir):
    tmpdir.mkdir('unrooted')
    tmpdir.join('unrooted', 'foo').write('bar')
    extract_test(tmpdir, 'unrooted.tar',
                 ['unrooted', 'unrooted/foo',
                  'unrooted-1', 'unrooted-1/a', 'unrooted-1/b'])


def test_untars_bz2(tmpdir):
    extract_test(tmpdir, 'rooted.tar.bz2',
                 ['root', 'root/a', 'root/b'])
