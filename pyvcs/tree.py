import os
import pathlib
import stat
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    tree=[]
    for i in index:
        if dirname:
            entry=dirname.split('/')
        else:
            entry=i.name.split('/')
        if len(entry)>1:
                mode="40000"
                record=f"{mode} {entry[0]}\0".encode()
                record += bytes.fromhex(write_tree(gitdir, index, f"/".join(entry[1:])))
                tree.append(record)
        elif i.name.find(dirname) != -1 :
            with open(i.name, 'rb') as f:
                data=f.read()
            record=f"{oct(i.mode)[2:]} {entry[-1]}\0".encode()
            record+=bytes.fromhex(hash_object(data,"blob",True))
            tree.append(record)
    tree_1 = b"".join(tree)
    return hash_object(tree_1, "tree", write=True)




def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    data=[]
    data.append(f"tree {tree}")
    if parent!=None:
        data.append(f"parent {parent}")
    if author == None:
        author = (os.environ("GIT_AUTHOR_NAME") + " " + f"<{os.environ('GIT_AUTHOR_EMAIL')}>")
    zone=abs(time.timezone)//60//60
    zone_s=abs(time.timezone)//60%60
    if time.timezone>0:
        zn='-'
    else:
        zn='+'
    if zone<10:
        zone='0'+str(zone)
    if zone_s<10:
        zone_s='0'+str(zone_s)
    timezone=zn+str(zone)+str(zone_s)
    data.append(f"author {author} {int(time.mktime(time.localtime()))} {timezone}")
    data.append(f"committer {author} {int(time.mktime(time.localtime()))} {timezone}")
    data.append(f"\n{message}\n")
    k=f"\n".join(data).encode()
    k1=hash_object(k,"commit",True)
    return k1

