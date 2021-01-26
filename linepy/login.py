from typing import Callable, Dict, Any
from lesting.api.client import build

class LoginResult:

    certificate: str
    accessToken: str
    lastBindTimestamp: int
    metaData: Dict[str, str]

class QRLogin:

    HOST = "https://legy-jp.line.naver.jp"
    PATH = HOST + "/acct/lgn/sq/v1"
    POLL = HOST + "/acct/lp/lgn/sq/v1"

    HEADERS = {
        "android_lite": {
            "user-agent": "LLA/2.12.0 SKR-H0 9",
            "x-line-application": "ANDROIDLITE\t2.12.0\tAndroid OS\t9;SECONDARY"
        },
        "android": {
            "user-agent": "Line/10.6.2",
            "x-line-application": "ANDROID\t10.6.2\tAndroid OS\t10"
        },
        "ios_ipad": {
            "user-Agent": "Line/10.1.1",
            "x-line-application": "IOSIPAD\t10.1.1\tiPhone 8\t11.2.5"
        },
        "ios": {
            "user-agent": "Line/10.1.1",
            "x-line-application": "IOS\t10.1.1\tiPhone 8\t11.2.5"
        },
        "chrome": {
            "user-agent": "MozilX-Line-Application/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
            "x-line-application": "CHROMEOS\t2.3.2\tChrome OS\t1"
        },
        "desktopwin": {
            "user-agent": "Line/5.12.3",
            "x-line-application": "DESKTOPWIN\t5.21.3\tWindows\t10"
        },
        "desktopmac": {
            "user-agent": "Line/5.12.3",
            "x-line-application": "DESKTOPMAC\t5.21.3\tMAC\t10.15"
        }
    }

    def __init__(self) -> None:
        self.client = build("line.login", "v1")

    def request(self, method: str, headers: Dict[str, str], *, lp: bool = False, **kwargs: Dict[str, Any]) -> Any:
        return getattr(self.client.parser, method)((self.client.http.request((self.POLL if lp else self.PATH), "POST", getattr(self.client.packer, method)(**kwargs), headers)[1]))

    def loginWithQrCode(self, application: str, certificate: str = "", web: bool = False, callback: Callable = lambda output: print(output)) -> LoginResult:
        headers = QRLogin.HEADERS[application]
        session = self.request("createSession", headers)
        result = self.request("createQrCode", headers, session = session)
        callback(result.url)
        if web:
            callback(result.web)
        self.request("checkQrCodeVerified", {**headers, **{"x-line-access": session}}, lp = True, session = session)
        try:
            self.request("verifyCertificate", headers, session = session, certificate = certificate)
        except:
            pin = self.request("createPinCode", headers, session = session)
            if web:
                self.client.pin.update(session, pin)
            else:
                callback(pin)
            self.request("checkPinCodeVerified", {**headers, **{"x-line-access": session}}, lp = True, session = session)
        return self.request("qrCodeLogin", headers, session = session, systemName = headers["x-line-application"].split("\t")[2], autoLoginIsRequired = True)

if __name__ == "__main__":
    qr = QRLogin()
    result = qr.loginWithQrCode("ipad", web = True)
    print("Access Token: " + result.accessToken)
    print("Certificate: " + result.certificate)
