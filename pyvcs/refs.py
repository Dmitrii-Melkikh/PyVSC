
import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    with open(gitdir/ref,"w") as f:
        f.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    with open(gitdir / name, "w") as f:
        f.write(ref)


def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:
    if refname=="HEAD" and not is_detached(gitdir):
        return resolve_head(gitdir)
    if (gitdir/refname).exists():
        with open(gitdir/refname) as f:
            return f.read()

def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    if is_detached(gitdir):
        with open(gitdir / "HEAD", "r")as f:
            return f.read()
    else:
        return ref_resolve(gitdir,get_ref(gitdir))

def is_detached(gitdir: pathlib.Path) -> bool:
    with open(gitdir/ "HEAD","r")as f:
        return len(f.read())==40



def get_ref(gitdir: pathlib.Path) -> str:
    with open(gitdir/"HEAD") as f:
        k = f.read()
    if k[:5] == "ref: ":
        k = k[5:-1]
    return k
