import socket
import threading
import inspect
import sys
import idaapi

from idacode_utils.safe_idaapi import SafeIDAAPI
from idacode_utils.safe_idautils import SafeIDAUtils
from idacode_utils.safe_idc import SafeIDC

HOST = "127.0.0.1"
PORT = 10100

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"IDACode listening on {HOST}:{PORT}")

    while True:
        io, _ = sock.accept()
        script = io.recv(256) # MAX_PATH
        io.close()

        if script and len(script) > 0:
            script = script.decode("utf8")
            print(f"Executing {script}")
            vars = {
                "idaapi": SafeIDAAPI(),
                "idc": SafeIDC(),
                "idautils": SafeIDAUtils(),
                "vscode_ida": True
            }
            idaapi.IDAPython_ExecScript(script, vars)

class VSCodeServer(idaapi.plugin_t):
    def __init__(self):
        self.flags = idaapi.PLUGIN_UNL
        self.comment = "IDACode"
        self.help = "IDACode"
        self.wanted_name = "Start IDACode"
        self.wanted_hotkey = ""

    def init(self):
        return idaapi.PLUGIN_OK

    def run(self, args):
        thread = threading.Thread(target=start_server)
        thread.daemon = True
        thread.start()

    def term(self):
        pass

def PLUGIN_ENTRY():
    return VSCodeServer()