import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    if "GIT_DIR" in os.environ:
        v=os.environ["GIT_DIR"]
    else:
        v=".pyvcs"
    way=pathlib.Path(workdir)
    way=way.absolute()
    k=0
    for dirpath, dirnames, filenames in os.walk(way):

        for i in dirnames:
            a = os.path.join(dirpath, i)
            if i==v:
                return (pathlib.Path(a))
                k=1
    l = os.path.dirname(way)
    while len(str(l))>1:
        b=os.listdir(l)
        if v in b:
            a=os.path.join(l,v)
            return (pathlib.Path(a))
            k=1
        l=os.path.dirname(l)
    if k==0:
        raise AssertionError("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    l=os.environ["GIT_DIR"] if "GIT_DIR" in os.environ else ".pyvcs"
    way=pathlib.Path(workdir)

    if way.is_file():
        raise Exception(f"{way} is not a directory")
    os.mkdir(l)
    with open(way / l / "HEAD", "w") as f:
        f.write("ref: refs/heads/master\n")
    with open(way/l/"config","w") as f:
        f.write("[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n")
    with open(way/l/"description","w") as f:
        f.write("Unnamed pyvcs repository.\n")
    (way /  l/ "objects").mkdir()
    (way / l/ "refs").mkdir()
    (way / l / "refs"/"tags").mkdir()
    (way / l/ "refs"/"heads").mkdir()
    return (way / l)