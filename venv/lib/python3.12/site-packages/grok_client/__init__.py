import pexpect
from threading import Thread
from os.path import expanduser, join, isfile
from tempfile import gettempdir
import signal
from subprocess import check_output
import platform
from enum import IntEnum
import yaml
import logging
import sys
from time import sleep


LOG = logging.getLogger("Ngrok")
LOG.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)


class NgrokException(Exception):
    """ something went wrong with ngrok"""


class NgrokStatus(IntEnum):
    LOADING = 0
    AUTHENTICATING = 10
    WAITING = 20
    RUNNING = 30
    FORWARDING = 40
    CONNECTED = 50
    CLOSED = 60
    FORBIDDEN = 70
    ERROR = 80
    STOP_REQUESTED = 90
    EXITED = 100
    INSTALLING = 110
    NOT_LOADED = 120


class Ngrok(Thread):
    def __init__(self, authtoken=None, config=None,
                 port=22, proto="tcp", debug=False):
        super().__init__()
        self.status = NgrokStatus.NOT_LOADED
        self.debug = debug
        self.proto = proto
        if config is not None:
            config = expanduser(config)
        self.config = config
        if debug:
            LOG.setLevel(logging.DEBUG)
        else:
            LOG.setLevel(logging.INFO)
        self.running = False
        self.port = str(port)
        self.ngrok = None
        self._prev_output = ""

        self.maybe_install()

        self.handle_status_change(NgrokStatus.LOADING)

        self.authtoken = authtoken
        self.handle_status_change(NgrokStatus.WAITING)

        self.host = None
        self.connection_port = None

        self._initial_conf = None

    @staticmethod
    def msg2dict(out):
        chunks = out.split(" ")
        keys = {}
        val = ""
        k = None
        for idx, msg in enumerate(chunks):
            if not msg:
                continue
            if "=" in msg:
                if k:
                    val = ""

                k = msg.split("=")[0]

                val = val + msg.split("=")[1]
                keys[k] = val
                keys[k] = val
            else:
                val = val + " " + msg
                keys[k] = val
        return keys

    def backup_config(self):
        if self.config is None:
            self._initial_conf = {}
        else:
            with open(self.config, "r") as f:
                self._initial_conf = yaml.load(f, Loader=yaml.SafeLoader)

    def restore_config(self):
        if self.config is not None:
            with open(self.config, "w") as f:
                yaml.dump(self._initial_conf, f)

    def override_config(self):
        if self.config is not None:
            conf_path = self.config
            with open(self.config, "r") as f:
                conf = yaml.load(f, Loader=yaml.SafeLoader)
        else:
            conf_path = join(gettempdir(), "ngrok.yml")
            conf = {}

        conf["log"] = "stdout"
        if self.authtoken:
            conf["authtoken"] = self.authtoken
        with open(conf_path, "w") as f:
            yaml.dump(conf, f)

    def maybe_install(self):
        try:
            check_output(["ngrok", "-h"])
            installed = True
        except FileNotFoundError:
            installed = False

        if installed:
            return

        self.handle_status_change(NgrokStatus.INSTALLING)

        is_arm = "x86_64" not in platform.platform()
        # TODO download binaries
        if is_arm:
            print("install arm")
        else:
            print("install linux")
        raise NgrokException("ngrok not installed")

    def handle_status_change(self, status):
        if self.debug:
            LOG.debug("Status {current} -> {new} ".format(
                current=self.status, new=status))
        self.status = status

    def handle_open(self, data):
        address = data["url"]
        LOG.info("Tunnel opened: " + str(address))
        self.host, self.connection_port = address.split("//")[1].split(":")

    def handle_connected(self, data):
        LOG.info("Tunnel Connection: " + data["r"])

    def handle_forbidden(self, data):
        LOG.warning("Forbidden: " + data["err"])

    def handle_stop_request(self, data):
        LOG.info("Exit Requested")

    def handle_closed(self, data):
        LOG.info("Tunnel closed")

    def handle_error(self, data):
        LOG.error(data["err"])
        raise NgrokException(data["msg"])

    def handle_status_info(self, data):
        LOG.debug("Status info: " + str(data))

    def launch(self) -> None:
        if not self.running:
            self.backup_config()
            self.override_config()

            self.running = True
            if self.config is not None:
                LOG.info("Starting ngrok from config " + self.config)
                if not isfile(self.config):
                    raise NgrokException("Config file does not exist")
                self.ngrok = pexpect.spawn('ngrok start -config {conf} '
                                           '--all'.format(conf=self.config))
            else:
                LOG.info("Starting ngrok {proto} {port}".format(
                    proto=self.proto, port=self.port))
                self.ngrok = pexpect.spawn('ngrok {proto} {port}'.format(
                    proto=self.proto, port=self.port))
            self.handle_status_change(NgrokStatus.RUNNING)
        else:
            LOG.error("Already running")
            raise NgrokException("Already running")

    def stop(self, ignore_exc=True) -> None:
        self.running = False
        self.restore_config()
        if self.ngrok is not None:
            self.ngrok.close()
            self.ngrok.kill(signal.SIGKILL)
            self.handle_status_change(NgrokStatus.EXITED)
            self.ngrok = None
        else:
            if not ignore_exc:
                LOG.error("Already stopped")
                raise NgrokException("Already stopped")

    def run(self):
        self.launch()
        while self.running:
            try:
                out = self.ngrok.readline().decode("utf-8")
                if out != self._prev_output:
                    out = out.strip()
                    if self.debug:
                        LOG.debug(out)
                    if "msg=" in out:
                        data = self.msg2dict(out)
                        self.handle_status_info(data)
                        if "err" in data:
                            if "failed to auth" in data["msg"] or \
                                    "TCP tunnels are only available after you sign up" in \
                                    data["err"]:
                                self.handle_status_change(
                                    NgrokStatus.FORBIDDEN)
                                self.handle_forbidden(data)
                                sleep(0.5)

                            self.handle_status_change(NgrokStatus.ERROR)
                            self.handle_error(data)

                        if data["obj"] == "tunnels" and \
                                "started tunnel" in data["msg"]:
                            self.handle_status_change(NgrokStatus.FORWARDING)
                            self.handle_open(data)
                        elif data["obj"] == "join" and \
                                "join connections" in data["msg"]:
                            self.handle_status_change(NgrokStatus.CONNECTED)
                            self.handle_connected(data)
                        elif "session closing" in data["msg"]:
                            self.handle_status_change(NgrokStatus.CLOSED)
                            self.handle_closed(data)
                        elif "received stop request" in data["msg"]:
                            self.handle_status_change(NgrokStatus.STOP_REQUESTED)
                            self.handle_stop_request(data)
                            self.running = False
                    self._prev_output = out

            except pexpect.exceptions.EOF:
                # ngrok exited
                self.running = False
            except pexpect.exceptions.TIMEOUT:
                # nothing happened for a while
                pass
            except NgrokException:
                self.running = False
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                LOG.exception(e)
                self.handle_status_change(NgrokStatus.ERROR)
                self.handle_error({"err": str(e),
                                   "msg": str(e)})
                raise
        self.quit()

    def quit(self):
        LOG.info("Exiting")
        self.stop(True)
        self.restore_config()
        LOG.debug("ngrok config restored")
