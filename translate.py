import requests
import execjs
import time
import random
from Crypto.Cipher import AES
from Crypto.Hash import MD5
import base64
import json


class YoudaoTranslater:
    def __init__(self, proxy=None) -> None:
        self.sess = requests.session()
        self.sess.proxies = proxy
        self.sess.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "origin": "https://fanyi.youdao.com",
            "referer": "https://fanyi.youdao.com/",
        }
        self.sess.cookies.set(
            "OUTFOX_SEARCH_USER_ID_NCOO",
            f"{random.randint(100000000, 999999999)}.{random.randint(100000000, 999999999)}",
        )
        self.sess.cookies.set(
            "OUTFOX_SEARCH_USER_ID",
            f"{random.randint(100000000, 999999999)}@{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        )
        params = {
            "keyid": "webfanyi-key-getter",
        } | self.__base_body("asdjnjfenknafdfsdfsd")
        res = self.sess.get("https://dict.youdao.com/webtranslate/key", params=params)
        t = res.json()
        self.key = t["data"]["secretKey"]

    def get_lan_list(self) -> dict:
        res = self.sess.get(
            "https://api-overmind.youdao.com/openapi/get/luna/dict/luna-front/prod/langType"
        )
        return res.json()["data"]["value"]["textTranslate"]

    def __sticTime(self) -> str:
        return str(int(time.time() * 1000))

    def __sign(self, t: str, key: str) -> str:
        return (
            MD5.new(
                f"client=fanyideskweb&mysticTime={t}&product=webfanyi&key={key}".encode()
            )
            .digest()
            .hex()
        )

    def __base_body(self, key: str) -> dict:
        t = self.__sticTime()
        return {
            "sign": self.__sign(t, key),
            "client": "fanyideskweb",
            "product": "webfanyi",
            "appVersion": "1.0.0",
            "vendor": "web",
            "pointParam": "client,mysticTime,product",
            "mysticTime": t,
            "keyfrom": "fanyi.web",
        }

    def __decode(self, src: str) -> dict:
        key = b"ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
        iv = b"ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
        cryptor = AES.new(
            MD5.new(key).digest()[:16], AES.MODE_CBC, MD5.new(iv).digest()[:16]
        )
        res = cryptor.decrypt(base64.urlsafe_b64decode(src))
        txt = res.decode("utf-8")
        return json.loads(txt[: txt.rindex("}") + 1])

    def translate(self, src: str, fromLan: str = "auto", toLan: str = "auto"):
        data = {
            "i": src,
            "from": fromLan,
            "to": toLan,
            "dictResult": True,
            "keyid": "webfanyi",
        } | self.__base_body(self.key)
        res = self.sess.post("https://dict.youdao.com/webtranslate", data=data)
        return self.__decode(res.text)


class Py4Js:
    def __init__(self):
        self.ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 

        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 

        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 

    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)

    def get_tk(self, text):
        return self.ctx.call("TL", text)


def request(url, params=None, proxy=None):
    while True:
        try:
            if proxy is not None:
                res = requests.get(url=url, params=params, proxies=proxy)
            else:
                res = requests.get(url=url, params=params)
            return res
        except Exception as e:
            print(e)
            time.sleep(1)


def google_translate(content, toLan="zh-CN", proxy=None, fromLan="auto"):
    content = content.replace('\n', '')
    err = 3
    while err > 0:
        js = Py4Js()
        tk = js.get_tk(content)
        if len(content) > 4891:
            return '输入请不要超过4891个字符!'
        param = {'tk': tk, 'q': content}
        url = """http://translate.google.com/translate_a/single?client=t&sl={} 
            &tl={}&hl={}&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss 
            &dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1&srcrom=0&ssel=0&tsel=0&kc=2""".format(fromLan, toLan, toLan)
        result = request(url=url, params=param, proxy=proxy)
        if result.status_code == 200:
            trans = result.json()[0]
            res = ''
            for i in range(len(trans)):
                line = trans[i][0]
                if line is not None:
                    res += trans[i][0]
            return res
        err -= 1