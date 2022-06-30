# -*- coding: UTF-8 -*-
import random
from typing import List

user_agent_list: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Edg/100.0.1185.39",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Edg/100.0.1185.39",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 OPR/87.0.4390.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 OPR/87.0.4390.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 OPR/87.0.4390.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 OPR/87.0.4390.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 "
    "YaBrowser/22.5.0 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 YaBrowser/22.5.0 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 YaBrowser/22.5.0 Yowser/2.5 Safari/537.36"
]


def get_ua():
    idx: int = random.choice(range(len(user_agent_list)))
    return user_agent_list[idx]
