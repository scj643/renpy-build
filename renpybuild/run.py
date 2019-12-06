import jinja2
import shlex
import subprocess
import sys
import sysconfig


def build_environment(c):
    """
    Sets up the build environment inside the context.
    """

    c.var("make", "make -j 6")

    c.var("sysroot", c.tmp / f"sysroot.{c.platform}-{c.arch}")
    c.var("build_platform", sysconfig.get_config_var("HOST_GNU_TYPE"))

    c.env("CPPFLAGS", "-I{{ install }}/include")
    c.env("CFLAGS", "-I{{ install }}/include")

    if (c.platform == "linux") and (c.arch == "x86_64"):
        c.var("host_platform", "x86_64-pc-linux-gnu")
    elif (c.platform == "linux") and (c.arch == "i686"):
        c.var("host_platform", "i686-pc-linux-gnu")

    if (c.kind == "host") or (c.kind == "cross"):

        c.env("CC", "ccache gcc")
        c.env("CXX", "ccache g++")
        c.env("CPP", "ccache gcc -E")
        c.env("AR", "ccache ar")
        c.env("RANLIB", "ccache ranlib")

    elif (c.platform == "linux") and (c.arch == "x86_64"):

        c.env("CC", "ccache gcc -m64 -O3 -fPIC -pthread --sysroot {{ sysroot }}")
        c.env("CXX", "ccache g++ -m64 -O3 -fPIC -pthread --sysroot {{ sysroot }}")
        c.env("CPP", "ccache gcc -m64 -E --sysroot {{ sysroot }}")
        c.env("AR", "ccache ar")
        c.env("RANLIB", "ccache ranlib")

        c.env("LDFLAGS", "-L{{ install }}/lib -L{{ install }}/lib64 -L{{ sysroot }}/lib -L{{ sysroot }}/usr/lib  -L{{ sysroot }}/usr/lib/x86_64-linux-gnu")

    elif (c.platform == "linux") and (c.arch == "i686"):

        c.env("CC", "ccache gcc -m32 -fPIC -O3 -pthread --sysroot {{ sysroot }}")
        c.env("CXX", "ccache g++ -m32 -fPIC -O3 -pthread --sysroot {{ sysroot }}")
        c.env("CPP", "ccache gcc -m32 -E --sysroot {{ sysroot }}")
        c.env("AR", "ccache ar")
        c.env("RANLIB", "ccache ranlib")

    c.env("LD", "{{ CC }}")
    c.env("LDXX", "{{ CXX }}")

    if c.kind != "host":
        c.var("cross_config", "--host={{ host_platform }} --build={{ build_platform }}")


def run(command, context, verbose=False):
    args = shlex.split(command)

    if verbose:
        print(" ".join(shlex.quote(i) for i in args))

    p = subprocess.run(args, cwd=context.cwd, env=context.environ)

    if p.returncode != 0:
        print(f"{context.task_name}: process failed with {p.returncode}.")
        print("args:", args)
        sys.exit(1)

