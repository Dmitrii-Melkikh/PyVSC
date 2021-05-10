import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    sha = hashlib.sha1((fmt + " " + str(len(data))).encode() + b"\0" + data).hexdigest()
    if write:
        way = repo_find()
        if not (way / "objects" / sha[:2]).exists():
            (way / "objects" / sha[:2]).mkdir()
        with open(way / "objects" / sha[:2] / sha[2:],"wb") as file:
            file.write(zlib.compress((fmt + " " + str(len(data))).encode() + b"\0" + data))
    return sha


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    list=[]
    if len(obj_name)<5 or len(obj_name)>39:
        raise Exception(f"Not a valid object name {obj_name}")
    l=(gitdir/"objects").glob("*")
    for i in l:
        l1=i.glob("*")
        for j in l1:
            full_name=j.parent.name+j.name
            if obj_name==full_name[:len(obj_name)]:
                list.append(full_name)
    if not list:
        raise Exception(f"Not a valid object name {obj_name}")
    return list



def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    ...


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    with open(gitdir/"objects"/sha[:2]/sha[2:], "rb") as f:
        d=zlib.decompress(f.read())
    l=[]
    k=d.find(b" ")
    l.append(d[:k].decode("ascii"))
    k=d.find(b"\x00")
    l.append(d[k+1:])
    return l



def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    tree = []

    while data:
        before_sha_ind = data.index(b"\00")
        mode, name = map(lambda x: x.decode(), data[:before_sha_ind].split(b" "))
        sha = data[before_sha_ind + 1 : before_sha_ind + 21]
        tree.append((int(mode), name, sha.hex()))
        data = data[before_sha_ind + 21 :]
    return tree


def cat_file(obj_name: str, pretty: bool = True) -> None:
    gitdir=repo_find()
    info=read_object(obj_name,gitdir)
    if info[0]=="commit" or info[0]=="blob":
        print(info[1].decode())
    else:
        for tree in read_tree(info[1]):
            if tree[0] == 40000:
                print(f"{tree[0]:06}", "tree", tree[2] + "\t" + tree[1])
            else:
                print(f"{tree[0]:06}", "blob", tree[2] + "\t" + tree[1])


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    fmt, data= read_object(tree_sha,gitdir)
    th=read_tree(data)
    l=[]
    for i in th:
        if i[0]!=100644:
            l1=find_tree_files(i[2],gitdir)
            for k in l1:
                l.append((i[1]+'/'+k[0],k[1]))
        else:
            l.append((i[1],i[2]))

    return l


def commit_parse(raw: bytes, start: int = 0, dct=None):
    ...