# -*- coding: utf-8 -*-
from akad.ttypes import IdentityProvider, LoginResultType, LoginRequest, LoginType
from .server import Server
from .session import Session
from .callback import Callback
#from BEAPI import *

import rsa, os, time, requests, random


list_lal = """ar_EG
ar_SA
zh_CN
zh_HK
zh_TW
en_US
en_AU
en_CA
en_GB
en_IE
en_IN
en_SG
en_ZA
fr_CA
fr_CH
de_DE
de_AT
hi_IN
id_ID
ja_JP
kn_CA
ko_KR
ms_MY
pt_BR
pt_PT
es_AR
es_CL
es_CO
es_CR
es_DO
es_EC
es_SV
es_GT
es_HN
es_MX
es_NI
es_PA
es_PE
es_PR
es_PY
es_US
es_UY
es_VE
tr_TR"""

androver = [
    "11.0.0",
    "10.0.0",
    "9.0.0",
    "8.1.0",
    "8.0.0",
    "7.1.2",
    "7.1.1",
    "7.1.0",
    "7.0.0",
    "6.0.1",
    "6.0.0",
    "5.1.1",
    "5.1.0",
    "5.0.2",
    "5.0.1",
    "5.0.0"
]

class Auth(object):
    isLogin     = False
    authToken   = ""
    certificate = ""

    def __init__(self):
        self.server = Server()
        self.callback = Callback(self.__defaultCallback)
        self.server.setHeadersWithDict({
            'User-Agent': self.server.USER_AGENT,
            'X-Line-Application': self.server.APP_NAME,
            #'X-Line-Carrier': self.server.CARRIER
            'x-lal': self.lal
        })

    def __loadSession(self, proxy=None):
        #print(f"APP NAME: {self.server.Headers['X-Line-Application']}")
        #print(f"USER AGENT: {self.server.Headers['User-Agent']}")
        #print(f"PROXY: {proxy}")
        #print(self.server.Headers)
        self.pollheader = {}
        self.pollheader.update(self.server.Headers)
        self.pollheader.update({
            "x-lac": "51010",
            "x-las": "F",
            "x-lam":"m",
        })
        #print(self.pollheader)
        #time.sleep(10)
        self.talk       = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_API_QUERY_PATH_FIR).Talk(proxy=proxy)
        self.poll       = Session(self.server.LINE_HOST_DOMAIN, self.pollheader, self.server.LINE_POLL_QUERY_PATH_FIR).Poll(proxy=proxy)
        #self.call       = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_CALL_QUERY_PATH).Call()
        self.channel    = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_CHAN_QUERY_PATH).Channel(proxy=proxy)
        #self.shop       = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_SHOP_QUERY_PATH).Shop()
        self.liff       = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_LIFF_QUERY_PATH).Liff(proxy=proxy)
        
        if "ANDROIDLITE" in self.server.Headers['X-Line-Application'] or "IOS" in self.server.Headers['X-Line-Application']:
            self.localRev = -1
            self.globalRev = 0
            self.individualRev = 0
            print("Send Flex")
        else:
            self.revision = self.poll.getLastOpRevision()
        self.isLogin = True


    def __loginRequest(self, type, data):
        lReq = LoginRequest()
        if type == '0':
            lReq.type = LoginType.ID_CREDENTIAL
            lReq.identityProvider = data['identityProvider']
            lReq.identifier = data['identifier']
            lReq.password = data['password']
            lReq.keepLoggedIn = data['keepLoggedIn']
            lReq.accessLocation = data['accessLocation']
            lReq.systemName = data['systemName']
            lReq.certificate = data['certificate']
            lReq.e2eeVersion = data['e2eeVersion']
        elif type == '1':
            lReq.type = LoginType.QRCODE
            lReq.keepLoggedIn = data['keepLoggedIn']
            if 'identityProvider' in data:
                lReq.identityProvider = data['identityProvider']
            if 'accessLocation' in data:
                lReq.accessLocation = data['accessLocation']
            if 'systemName' in data:
                lReq.systemName = data['systemName']
            lReq.verifier = data['verifier']
            lReq.e2eeVersion = data['e2eeVersion']
        else:
            lReq=False
        return lReq

    def loginWithCredential(self, _id, passwd, certificate=None, systemName=None, appName=None, keepLoggedIn=True, proxy=None):
        #print(f"EMAIL LOGIN PROXY: {proxy}")
        if systemName is None:
            systemName=self.server.SYSTEM_NAME
        if self.server.EMAIL_REGEX.match(_id):
            self.provider = IdentityProvider.LINE       # LINE
        else:
            self.provider = IdentityProvider.NAVER_KR   # NAVER
        
        if appName is None:
            appName=self.server.APP_NAME
        self.server.setHeaders('X-Line-Application', appName)
        self.tauth = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_AUTH_QUERY_PATH).Talk(isopen=False, proxy=proxy)

        rsaKey = self.tauth.getRSAKeyInfo(self.provider)
        
        message = (chr(len(rsaKey.sessionKey)) + rsaKey.sessionKey +
                   chr(len(_id)) + _id +
                   chr(len(passwd)) + passwd).encode('utf-8')
        pub_key = rsa.PublicKey(int(rsaKey.nvalue, 16), int(rsaKey.evalue, 16))
        crypto = rsa.encrypt(message, pub_key).hex()

        try:
            with open(_id + '.crt', 'r') as f:
                self.certificate = f.read()
        except:
            if certificate is not None:
                self.certificate = certificate
                if os.path.exists(certificate):
                    with open(certificate, 'r') as f:
                        self.certificate = f.read()

        self.auth = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_LOGIN_QUERY_PATH).Auth(isopen=False, proxy=proxy)

        lReq = self.__loginRequest('0', {
            'identityProvider': self.provider,
            'identifier': rsaKey.keynm,
            'password': crypto,
            'keepLoggedIn': keepLoggedIn,
            'accessLocation': self.server.IP_ADDR,
            'systemName': systemName,
            'certificate': self.certificate,
            'e2eeVersion': 0
        })

        result = self.auth.loginZ(lReq)
        
        if result.type == LoginResultType.REQUIRE_DEVICE_CONFIRM:
            self.callback.PinVerified(result.pinCode, _id)

            self.server.setHeaders('X-Line-Access', result.verifier)
            getAccessKey = self.server.getJson(self.server.parseUrl(self.server.LINE_CERTIFICATE_PATH), allowHeader=True)

            self.auth = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_LOGIN_QUERY_PATH).Auth(isopen=False, proxy=proxy)

            try:
                lReq = self.__loginRequest('1', {
                    'keepLoggedIn': keepLoggedIn,
                    'verifier': getAccessKey['result']['verifier'],
                    'e2eeVersion': 0
                })
                result = self.auth.loginZ(lReq)
            except:
                raise Exception('Login failed')
            
            if result.type == LoginResultType.SUCCESS:
                if result.certificate is not None:
                    with open(_id + '.crt', 'w') as f:
                        f.write(result.certificate)
                    self.certificate = result.certificate
                if result.authToken is not None:
                    self.loginWithAuthToken(result.authToken, appName, proxy=proxy)
                else:
                    return False
            else:
                raise Exception('Login failed')

        elif result.type == LoginResultType.REQUIRE_QRCODE:
            self.loginWithQrCode(keepLoggedIn, systemName, appName)
            pass

        elif result.type == LoginResultType.SUCCESS:
            self.certificate = result.certificate
            self.loginWithAuthToken(result.authToken, appName, proxy=proxy)

    def loginWithQrCode(self, keepLoggedIn=True, systemName=None, appName=None, showQr=False, proxy=None):
        if systemName is None:
            systemName=self.server.SYSTEM_NAME
        if appName is None:
            appName=self.server.APP_NAME
        self.server.setHeaders('X-Line-Application', appName)

        self.tauth = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_AUTH_QUERY_PATH).Talk(isopen=False, proxy=proxy)
        qrCode = self.tauth.getAuthQrcode(keepLoggedIn, systemName)

        self.callback.QrUrl('line://au/q/' + qrCode.verifier, showQr)
        self.server.setHeaders('X-Line-Access', qrCode.verifier)

        getAccessKey = self.server.getJson(self.server.parseUrl(self.server.LINE_CERTIFICATE_PATH), allowHeader=True)
        
        self.auth = Session(self.server.LINE_HOST_DOMAIN, self.server.Headers, self.server.LINE_LOGIN_QUERY_PATH).Auth(isopen=False, proxy=proxy)
        
        try:
            lReq = self.__loginRequest('1', {
                'keepLoggedIn': keepLoggedIn,
                'systemName': systemName,
                'identityProvider': IdentityProvider.LINE,
                'verifier': getAccessKey['result']['verifier'],
                'accessLocation': self.server.IP_ADDR,
                'e2eeVersion': 0
            })
            result = self.auth.loginZ(lReq)
        except:
            raise Exception('Login failed')

        if result.type == LoginResultType.SUCCESS:
            if result.authToken is not None:
                self.loginWithAuthToken(result.authToken, appName)
            else:
                return False
        else:
            raise Exception('Login failed')

    def GenerateModel(self):
        random.seed = (os.urandom(1024))
        tipe= "".join(random.choice("1234567890") for i in range(5))
        return random.choice(["GT-", "GF-", "YT-", "GA-", "GU-", "GW-", "Y-", "V-", "S-", "T-", "P-", "Q-", "Z-"]) + tipe

    def loginWithAuthToken(self, authToken=None, appName=None, proxy=None):
        if authToken is None:
            raise Exception('Please provide Auth Token')
        if appName is None:
            appName=self.server.APP_NAME

        userAgent = ""
        appSplit = appName.split("\t")
        if appSplit[0] == "ANDROIDLITE":
            lite = ["2.13.0", "2.13.1","2.13.2", "2.14.0", "2.15.0", "2.16.0", "2.17.0"]
            appName = f"ANDROIDLITE\t{random.choice(lite)}\tAndroid OS\t{random.choice(androver)}"
            appSplit = appName.split("\t")
            userAgent = 'LLA/{} {} {}'.format(appSplit[1],self.GenerateModel(), appSplit[3])

        elif appSplit[0] == "CHROMEOS":
            chrome = ["2.4.0", "2.4.1", "2.4.2", "2.4.3"]
            #api = BEAPI(requests.get("https://fgmid.xyz/apibe_fgm.php").text)
            res = requests.get("https://sczit.xyz/ua_chrome.php").json()["result"]
            #res = api.lineAppnameRandom("chromeos")["result"]
            userAgent = res["User-Agent"]
            appName = res["X-Line-Application"]
            appName = appName.replace(appName.split("\t")[1], random.choice(chrome))
            
        elif appSplit[0]  in ["IOS"]:
            dataUserAgent = ""
            dataHeader = random.choice(["12.21.0"])
            for x in range(5):
                angka = ["1", "2", "3", "4", "5"]
                ver = random.choice(angka)
                dataUserAgent += ver
            appName = "IOS\t"+dataHeader+"\tiOS\t15.5"
            userAgent = 'Line/'+dataHeader+' iOS 15.5 iPhone X'

        else:
            userAgent = 'Line/%s' % appSplit[1]

        self.server.setHeadersWithDict({
            'X-Line-Application': appName,
            'X-Line-Access': authToken,
            'User-Agent': userAgent
        })
        if self.spoof != None:
          self.server.setHeadersWithDict({'X-Forwarded-For': self.spoof})
        self.authToken = authToken
        self.__loadSession(proxy=proxy)

    def __defaultCallback(self, str):
        print(str)

    def logout(self):
        self.auth.logoutZ()
