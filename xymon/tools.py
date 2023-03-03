"""
Wrappers for xymon command line tools.

"""
import os
import subprocess
import sys
from typing import NamedTuple, List


class TaggedHost(NamedTuple):
    """Host with test configuration as identified by a tag in hosts.cfg

    `params` contains any parameters that where found as comma separated values
    after the test tag. Example: if hosts.cfg specifies `mytag=1,2,3` then `params` 
    will contain ['1', '2', '3'].
    """
    host: str
    ip: str
    params: List[str]


def find_tagged_hosts(tag: str) -> List[TaggedHost]:
    """Look for tag in hosts.cfg and return matching hosts

    This function wraps `xymongrep` to parse and return all test configs 
    identified by `tag` in hosts.cfg, traversing includes. The tag may include
    a wildcard character ("mytag=*") which is useful if the tag is followed 
    by additional parameters, e.g. `mytag=val1,val2,...` (see docstring for
    :class:`TestConfig`).

    tag: Tag to look for in hosts.cfg.

    """
    cfg = run_xymon_cmd('xymongrep', '--noextras', tag)
    results = []
    for line in cfg.splitlines():
        tokens = line.split()
        tag_token = tokens[3]
        params = []
        if '=' in tag_token:
            params = tag_token.split('=', maxsplit=1)[1].split(',')
        results.append(TaggedHost(host=tokens[1], ip=tokens[0], params=params))
    return results


def run_xymon_cmd(cmd: str, *args: str) -> str:
    """Run a xymon command and return its output

    Returns the output of `cmd` from stdout encoded as an utf-8 string.

    cmd:   Command (tool) to run from the xymon bin directory.
    args:  These are passed to the cmd verbatim.

    """
    path = os.path.join(os.environ['XYMONHOME'], 'bin', cmd)
    try:
        result = subprocess.run([path, *args], check=True, encoding='utf-8',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as ex:
        print(f"Error while executing {ex.cmd}: ({ex.returncode}) {ex.stderr}",
              file=sys.stderr)
        raise
    return result.stdout
