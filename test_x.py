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


def test_untars_rooted(tmpdir):
    tmpdir.chdir()
    test_dir.join('rooted.tar').copy(tmpdir.join('rooted.tar'))
    assert main(['rooted.tar']) == 0
    assert paths(tmpdir) == set(['rooted.tar', 'root', 'root/a', 'root/b'])


def test_untars_unrooted(tmpdir):
    tmpdir.chdir()
    test_dir.join('unrooted.tar').copy(tmpdir.join('unrooted.tar'))
    assert main(['unrooted.tar']) == 0
    assert paths(tmpdir) == set(['unrooted.tar', 'unrooted', 'unrooted/a', 'unrooted/b'])
