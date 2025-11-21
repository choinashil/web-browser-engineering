import socket
import ssl


class URL:
    def __init__(self, url):
        self.scheme, url = url.split('://', 1)
        print(self.scheme)
        print(url)

        assert self.scheme in ['http', 'https']

        # http, https 처리 추가
        if self.scheme == 'http':
            self.port = 80
        elif self.scheme == 'https':
            self.port = 443

        # host와 url 분리
        if '/' not in url:
            url = url + '/'
        self.host, url = url.split('/', 1)

        # 커스텀 포트 처리 (예: example.com:8080)
        # host에서 포트 분리
        if ':' in self.host:
            self.host, port = self.host.split(':', 1)
            self.port = int(port)

        # path 설정
        self.path = '/' + url

    def request(self):
        s = socket.socket(
            # Address Family 참고: docs/address-family.md
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        # TCP 연결 사 scheme에 따른 port 전달
        s.connect((self.host, self.port))

        # TCP 연결 후 SSL 래핑
        # - SSL 핸드셰이크는 TCP 연결 수립 이후에 이루어짐
        # - TCP 연결 없이는 SSL 암호화를 할 수 없음
        # - 참고: docs/tcp-ssl-handshake.md
        if self.scheme == 'https':
            # 기본 SSL/TLS 설정을 가진 컨텍스트 생성 (인증서 검증 활성화)
            # 참고: docs/ssl-tls.md
            ctx = ssl.create_default_context()
            # 일반 TCP 소켓을 SSL/TLS로 래핑하여 암호화된 소켓으로 변환
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # 서버에 요청 전송
        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers  # 청크
        assert "content-encoding" not in response_headers  # 압축

        body = response.read()
        s.close()

        return body


def show(body):
    in_tag = False
    for c in body:
        if c == '<':
            in_tag = True
        elif c == '>':
            in_tag = False
        elif not in_tag:
            print(c, end="")


def load(url):
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys
    url = URL(sys.argv[1])
    load(url)
