import socket


class URL:
    def __init__(self, url):
        self.scheme, url = url.split('://', 1)
        print(self.scheme)
        print(url)

        assert self.scheme == 'http'

        if '/' not in url:
            url = url + '/'
        self.host, url = url.split('/', 1)
        self.path = '/' + url

    def request(self):
        s = socket.socket(
            # Address Family 참고: docs/address-family.md
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        # TCP 연결
        # - 서버와 연결은 되었지만
        # - 아무것도 요청하지 않음
        # - 서버는 클라이언트가 뭔가 보내길 기다림
        # - 클라이언트는 아무것도 안 보내고 함수 종료
        # - 연결이 닫힘
        s.connect((self.host, 80))

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
