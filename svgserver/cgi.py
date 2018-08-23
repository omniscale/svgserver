import errno
import os
import re
import time

from io import BytesIO

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


import subprocess

import logging

log = logging.getLogger(__name__)


def split_cgi_response(data):
    headers = []
    prev_n = 0
    while True:
        next_n = data.find(b"\n", prev_n)
        if next_n < 0:
            break
        next_line_begin = data[next_n + 1 : next_n + 3]
        headers.append(data[prev_n:next_n].rstrip(b"\r"))
        if next_line_begin[0:1] == b"\n":
            return headers_dict(headers), data[next_n + 2 :]
        elif next_line_begin == b"\r\n":
            return headers_dict(headers), data[next_n + 3 :]
        prev_n = next_n + 1
    return {}, data


def headers_dict(header_lines):
    headers = {}
    for line in header_lines:
        if b":" in line:
            key, value = line.split(b":", 1)
            value = value.strip()
        else:
            key = line
            value = None
        key = key.decode("latin-1")
        key = key[0].upper() + key[1:].lower()
        if value:
            value = value.decode("latin-1")
        headers[key] = value
    return headers


class IOwithHeaders(object):
    def __init__(self, io, headers):
        self.io = io
        self.headers = headers

    def __getattr__(self, name):
        return getattr(self.io, name)


def find_exec(executable):
    """
    Search executable in PATH environment. Return path if found, None if not.
    """
    path = os.environ.get("PATH")
    if not path:
        return
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, executable)
        if os.path.exists(p):
            return p
        p += ".exe"
        if os.path.exists(p):
            return p


class CGIClient(object):
    def __init__(self, script, no_headers=False, working_directory=None):
        self.script = script
        if not os.path.exists(script):
            self.script = find_exec(script)
        if self.script is None:
            raise ValueError("script '%s' not found" % script)
        self.working_directory = working_directory
        self.no_headers = no_headers

    def get(self, params):
        query = urlencode(params)
        environ = os.environ.copy()
        environ.update(
            {
                "QUERY_STRING": query,
                "REQUEST_METHOD": "GET",
                "GATEWAY_INTERFACE": "CGI/1.1",
                "SERVER_ADDR": "127.0.0.1",
                "SERVER_NAME": "localhost",
                "SERVER_PROTOCOL": "HTTP/1.0",
                "SERVER_SOFTWARE": "CGIClient",
            }
        )

        start_time = time.time()
        p = subprocess.Popen(
            [self.script],
            env=environ,
            stdout=subprocess.PIPE,
            cwd=self.working_directory or os.path.dirname(self.script),
        )

        stdout = p.communicate()[0]
        ret = p.wait()
        if ret != 0:
            raise HTTPClientError("Error during CGI call (exit code: %d)" % (ret,))

        if self.no_headers:
            content = stdout
            headers = dict()
        else:
            headers, content = split_cgi_response(stdout)

        status_match = re.match("(\d\d\d) ", headers.get("Status", ""))
        if status_match:
            status_code = status_match.group(1)
        else:
            status_code = "-"
        size = len(content)
        content = IOwithHeaders(BytesIO(content), headers)

        log.debug(
            "%s:%s took %dkb %dms",
            self.script,
            query,
            size / 1024.0,
            (time.time() - start_time) * 1000,
        )
        return content
