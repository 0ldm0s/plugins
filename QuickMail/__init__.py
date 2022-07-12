# -*- coding: UTF-8 -*-
import re
import dkim
import time
import base64
import inspect
import smtplib
import threading
from flask import render_template_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from typing import List, Optional, Dict, Any
from mio.util.Logs import LogHandler


class QuickMail:
    VERSION = '0.2'
    sender: str = ""
    recipients: List[str] = []
    content_type: str = "plain"
    threads: int = 1
    hostname: str = ""
    results: List[Dict[str, Any]] = []
    port: int = smtplib.SMTP_PORT
    nameservers: Optional[List[str]] = None
    dkim_private_key_path: Optional[str] = None
    dkim_selector: Optional[str] = None

    def __get_logger__(self, name: str) -> LogHandler:
        name = '{}.{}'.format(self.__class__.__name__, name)
        return LogHandler(name)

    class ActivePool(object):
        def __init__(self):
            self.active = []
            self.lock = threading.Lock()

        def make_active(self, name):
            with self.lock:
                self.active.append(name)

        def make_inactive(self, name):
            with self.lock:
                self.active.remove(name)

        def num_active(self):
            with self.lock:
                return len(self.active)

        def __str__(self):
            with self.lock:
                return str(self.active)

    @staticmethod
    def __get_domain__(recipient) -> Optional[str]:
        m = re.match(r'.+@(.+)', recipient)
        if m:
            return m.group(1)
        else:
            return None

    def query_mxrecords(self, domain: str) -> List[str]:
        """
        Looks up for the MX DNS records of the recipient SMTP server
        """
        console_log: LogHandler = self.__get_logger__(inspect.stack()[0].function)
        import dns.resolver
        console_log.info('正在查询DNS数据……')
        my_resolver = dns.resolver.Resolver()
        if self.nameservers is not None:
            my_resolver.nameservers = self.nameservers
        answers = my_resolver.resolve(domain, 'MX')
        addresses: List[str] = [answer.exchange.to_text() for answer in answers]
        console_log.info(
            '共有 {} 条记录:\n{}'.format(
                len(addresses), '\n  '.join(addresses)))
        return addresses

    def postman(self, pool: ActivePool, recipient: str, msg: MIMEText):
        name = threading.current_thread().name
        console_log: LogHandler = self.__get_logger__(inspect.stack()[0].function)
        console_log.info(f"线程[{name}]开始执行")
        pool.make_active(name)
        try:
            if len(recipient) == 0:
                return
            domain: Optional[str] = self.__get_domain__(recipient)
            if domain is None:
                self.results.append({
                    "recipient": recipient,
                    "result": False,
                    "errormsg": "非有效域名"
                })
                return
            addresses: List[str] = self.query_mxrecords(domain)
            if len(addresses) == 0:
                self.results.append({
                    "recipient": recipient,
                    "result": False,
                    "errormsg": "该域名未配置MX"
                })
                return
            result: bool = False
            errormsg: str = ""
            for mx in addresses:
                try:
                    console_log.info(f"[{name}]正在连线[{mx}:{self.port}]")
                    server = smtplib.SMTP(mx, self.port, local_hostname=self.hostname, timeout=10)
                    server.ehlo(self.hostname)
                    server.sendmail(from_addr=self.sender, to_addrs=[recipient], msg=msg.as_bytes())
                    server.quit()
                    result = True
                    break
                except Exception as e:
                    console_log.error(e)
                    errormsg = str(e)
            self.results.append({
                "recipient": recipient,
                "result": result,
                "errormsg": errormsg
            })
        except Exception as e:
            console_log.error(e)
            self.results.append({
                "recipient": recipient,
                "result": False,
                "errormsg": str(e)
            })
        finally:
            pool.make_inactive(name)
            console_log.info(f"线程[{name}]执行完毕")

    def __init__(
            self, sender: str, hostname: str, recipients: List[str], port: int = smtplib.SMTP_PORT,
            dkim_private_key_path: Optional[str] = None, dkim_selector: Optional[str] = None,
            content_type: str = "plain", threads: int = 1, nameservers: Optional[List[str]] = None
    ):
        self.sender = sender
        self.hostname = hostname
        self.recipients = recipients
        self.port = port
        self.dkim_private_key_path = dkim_private_key_path
        self.dkim_selector = dkim_selector
        self.content_type = content_type
        self.threads = threads
        self.nameservers = nameservers

    def send(
            self, summary: str, main_text: str, subject: str, charset: str = "UTF-8", timeval: Optional[int] = None,
            localtime: bool = True, **args
    ):
        idx: int = 0
        default_count: int = threading.active_count()
        work_pool = self.ActivePool()
        while True:
            current_count: int = threading.active_count() - default_count
            if current_count >= self.threads:
                time.sleep(1)
                continue
            if idx >= len(self.recipients):
                break
            recipient = self.recipients[idx]
            idx += 1
            mail_summary: bytes = render_template_string(summary, **args).encode(charset, "ignore")
            mail_text: bytes = render_template_string(main_text, **args).encode(charset, "ignore")
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(base64.b64encode(mail_summary), "plain", charset))
            msg.attach(MIMEText(base64.b64encode(mail_text), "html", charset))
            msg.add_header("Content-Transfer-Encoding", "base64")
            msg.add_header('X-Mailer', f"PyMio/PostMan.{self.VERSION}")
            msg.add_header('Precedence', 'bulk')
            msg["Subject"] = subject
            msg['Message-ID'] = make_msgid()
            msg["From"] = self.sender
            msg["To"] = recipient
            msg["Cc"] = ""
            msg["Bcc"] = ""
            msg["Date"] = formatdate(timeval, localtime)
            msg_data: bytes = msg.as_bytes()
            if self.dkim_private_key_path and self.dkim_selector:
                with open(self.dkim_private_key_path) as fh:
                    dkim_private_key = fh.read()
                headers = [b"To", b"From", b"Subject"]
                sig = dkim.sign(
                    message=msg_data,
                    selector=str(self.dkim_selector).encode(charset),
                    domain=self.hostname.encode(charset),
                    privkey=dkim_private_key.encode(charset),
                    include_headers=headers,
                )
                msg["DKIM-Signature"] = sig[len("DKIM-Signature: "):].decode(charset)
            job = threading.Thread(
                target=self.postman, name=f"postman-{idx}", args=(
                    work_pool, recipient, msg))
            job.daemon = True
            job.start()
        return self.results
