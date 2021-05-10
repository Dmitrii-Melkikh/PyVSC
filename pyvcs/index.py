import hashlib
import operator
import os
import pathlib
import struct
import typing as tp
from operator import attrgetter
from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        values=(self.ctime_s,self.ctime_n,self.mtime_s,self.mtime_n,self.dev,self.ino,self.mode,self.uid,self.gid,
                self.size,self.sha1,self.flags,self.name.encode())
        return struct.pack("!LLLLLLLLLL20sH"+str(len(self.name))+"s"+str(8-(62+len(self.name))%8)+"x",*values)

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        k=struct.unpack("!LLLLLLLLLL20sH"+str(len(data)-62)+"s",data)

        return GitIndexEntry(*k[:-1],k[-1].rstrip(b'\00').decode())


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    l=[]
    if not (gitdir/"index").exists():
        return []
    with open(gitdir / "index","rb") as f:
        head = f.read(12)
        index = f.read()
    k=struct.unpack('!L',head[8:])
    for i in range(k[0]):
        end=len(index)-1
        for j in range(63,len(index),8):
            if index[j]==0:
                end=j
                break
        l.append(GitIndexEntry.unpack(index[:end+1]))
        if len(index) != end - 1:
            index = index[end + 1:]

    return l





def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    head=struct.pack("!4sLL", b"DIRC",2,len(entries))
    data=b""
    for i in entries:
        data=data+GitIndexEntry.pack(i)
    sha = hashlib.sha1(head + data).digest()
    with open(gitdir/"index", "wb") as f:
        f.write(head+data+sha)



def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    if details==False:
        l=read_index(gitdir)
        for i in l:
            print(i.name)
    else:
        l=read_index(gitdir)
        for i in l:
            v=oct(i.mode)[2:]
            print(f"{v} {i.sha1.hex()} 0\t{i.name}")

def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    k=[]
    for i in paths:
        l=os.stat(i)
        with open(i, "rb") as f:
            data=f.read()
        sha=hash_object(data,"blob",True)
        k.append(

                 GitIndexEntry(
                    int(l.st_ctime),
                    (int(str(l.st_ctime_ns)[-1]) ),
                    int(l.st_mtime),
                    int(str(l.st_mtime_ns)[-1]),
                    l.st_dev,
                    l.st_ino,
                    l.st_mode,
                    l.st_uid,
                    l.st_gid,
                    l.st_size,
                    bytes.fromhex(sha),
                    7,
                    str(i).replace('\\','/'),
                )

        )
    if write:
        k.sort(key= lambda x:x[-1])
        write_index(gitdir,k)






        


