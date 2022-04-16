import shutil
from pathlib import Path

import pytest

from annotation import lib


VERBOSE = True
TEMPDIR = "./testtemp"
CONFIGFILE = TEMPDIR + "/config.ini"


@pytest.fixture(scope="class", autouse=True)
def tempdir():
    tempdirpath = Path(TEMPDIR).resolve()
    if tempdirpath.is_dir():
        shutil.rmtree(str(tempdirpath))
    tempdirpath.mkdir(exist_ok=False)

    yield None

    shutil.rmtree(str(tempdirpath))


@pytest.fixture(scope="function", autouse=False)
def sampleconfig():
    config =  dict(
        DEFAULT = dict(
            x = "xdef",
        ),
        a = dict(
            x = "ax",
            y = "ay",
        ),
        b = dict(
            x = "bx",
            y = "by",
        ),
    )
    lib.config.save(config, file=CONFIGFILE, mode="overwrite")
    yield config
    Path(CONFIGFILE).unlink()


class TestConfig(object):
    def test_load(self, sampleconfig):
        assert lib.config.load(file=CONFIGFILE) == sampleconfig

    def test_save_overwrite(self, sampleconfig):
        config = dict(hoge=dict(fuga=5))
        config_str = dict(hoge=dict(fuga="5"))
        lib.config.save(config, file=CONFIGFILE, mode="overwrite")
        c = lib.config.load(file=CONFIGFILE)
        assert lib.config.load(file=CONFIGFILE) == config_str

    # def test_save_add(self, sampleconfig):

    # def test_save_leave(self, sampleconfig):
