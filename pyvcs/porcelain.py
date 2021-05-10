import os
import pathlib
import typing as tp

from pyvcs.index import read_index, update_index  # type: ignore
from pyvcs.objects import commit_parse  # type: ignore
from pyvcs.objects import find_object  # type: ignore
from pyvcs.objects import find_tree_files  # type: ignore
from pyvcs.objects import read_object  # type: ignore
from pyvcs.objects import read_tree  # type: ignore
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref  # type: ignore
from pyvcs.tree import commit_tree, write_tree  # type: ignore


def add(gitdr: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    for path in paths:
        if path.is_file():
            update_index(gitdr, [path], write=True)
        if path.is_dir():
            add(gitdr, list(path.glob("*")))


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    tree=write_tree(gitdir,read_index(gitdir))
    comm=commit_tree(gitdir,tree,message,author=author)
    if is_detached(gitdir):
        vet = gitdir / "HEAD"
    else:
        vet = pathlib.Path(get_ref(gitdir))
    with open(gitdir/vet,"w") as f:
        f.write(comm)
    return comm


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    ref = get_ref(gitdir)
    if os.path.isfile(gitdir/ref):
        with open(gitdir/ref, "r") as f:
            ref = f.read()
    fmt, data = read_object(ref, gitdir)
    dirs = gitdir.absolute().parent
    data = data.decode()
    th = find_tree_files(data[5:45], gitdir)

    for i in th:
        os.remove(dirs / i[0])
        next = pathlib.Path(i[0]).parent
        while len(next.parents) > 0:
            os.rmdir(next)
            next = pathlib.Path(next).parent
    with open(gitdir/"HEAD","w") as f:
        f.write(obj_name)
    fmt, new = read_object(obj_name, gitdir)
    new = new.decode()
    th = find_tree_files(new[5:45], gitdir)
    for i in th:
        k = len(pathlib.Path(i[0]).parents)
        par_path = dirs
        for par in range(k - 2, -1, -1):
            par_path /= pathlib.Path(i[0]).parents[par]
            if not os.path.isdir(par_path):
                os.mkdir(par_path)
        fmt, obj_content = read_object(i[1], gitdir)
        if fmt == "blob":
            pathlib.Path(dirs / i[0]).touch()
            with open(dirs/i[0],"w") as f:
                f.write(obj_content.decode())
        else:
            os.mkdir(dirs / i[0])