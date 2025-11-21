# TCP와 SSL 핸드셰이크

## TCP와 SSL의 계층 구조

```
애플리케이션 계층   HTTP 요청/응답
                    ↓↑
전송 보안 계층      SSL/TLS (HTTPS일 때)
                    ↓↑
전송 계층          TCP 연결
                    ↓↑
네트워크 계층       IP
```

## 1. TCP (Transmission Control Protocol)

**역할**: 신뢰할 수 있는 데이터 전송 통로를 만듦

### TCP 연결 과정 (3-way handshake)

```
클라이언트                    서버
   |                           |
   |------- SYN -------------->|  1. 연결 요청
   |<----- SYN-ACK ------------|  2. 연결 수락
   |------- ACK -------------->|  3. 확인
   |                           |
   [TCP 연결 수립 완료]
```

**TCP가 하는 일:**
- 데이터가 순서대로 도착하는지 확인
- 손실된 데이터 재전송
- **하지만 암호화는 안 됨** (누구나 내용을 볼 수 있음)

## 2. SSL/TLS (Secure Sockets Layer / Transport Layer Security)

**역할**: TCP 위에서 암호화된 통신 제공

### 왜 TCP 이후에 SSL이 와야 하나?

- SSL은 TCP라는 **이미 만들어진 통로** 위에 **암호화 레이어**를 추가하는 것
- 통로(TCP)가 없으면 암호화할 데이터를 보낼 수 없음

**비유:**
- TCP = 도로를 건설하는 것
- SSL = 도로 위에 보안 터널을 만드는 것
- 도로(TCP)가 없으면 터널(SSL)을 만들 수 없음!

## 3. SSL 핸드셰이크 과정

TCP 연결 후에 일어나는 과정:

```
클라이언트                                서버
   |                                      |
   [TCP 연결 이미 수립됨]
   |                                      |
   |------- ClientHello ---------------->|  1. "SSL로 통신하고 싶어요"
   |                                      |     (지원하는 암호화 방식 목록)
   |                                      |
   |<------ ServerHello -----------------|  2. "OK, 이 방식 쓸게요"
   |<------ Certificate -----------------|     (서버 인증서 전달)
   |<------ ServerHelloDone -------------|
   |                                      |
   |------- ClientKeyExchange ---------->|  3. 암호화 키 교환
   |------- ChangeCipherSpec ----------->|
   |------- Finished ------------------->|
   |                                      |
   |<------ ChangeCipherSpec ------------|  4. 암호화 시작 확인
   |<------ Finished --------------------|
   |                                      |
   [SSL 핸드셰이크 완료, 암호화 통신 시작]
```

**핸드셰이크가 하는 일:**
1. 서버가 진짜인지 확인 (인증서 검증)
2. 어떤 암호화 방식을 쓸지 협상
3. 암호화에 필요한 비밀 키 교환

## 4. 전체 흐름 (HTTPS 요청)

```python
# 1단계: TCP 연결 (암호화 없음)
s = socket.socket(...)
s.connect((self.host, 443))  # TCP 3-way handshake
# ✅ 이제 서버와 데이터를 주고받을 수 있는 통로가 생김

# 2단계: SSL 래핑 (암호화 추가)
ctx = ssl.create_default_context()
s = ctx.wrap_socket(s, server_hostname=self.host)
# ✅ 내부적으로 SSL 핸드셰이크 실행
# ✅ 이제 통로가 암호화됨

# 3단계: HTTP 요청 (암호화된 통로로 전송)
s.send(request.encode("utf8"))
# ✅ 데이터가 암호화되어 전송됨
```

## 5. 왜 순서가 중요한가?

```python
# ❌ 잘못된 순서
s = socket.socket(...)
s = ctx.wrap_socket(s, ...)  # 에러! TCP 연결이 없음
s.connect(...)  # 이미 늦음

# ✅ 올바른 순서
s = socket.socket(...)
s.connect(...)               # 1. TCP 통로 만들기
s = ctx.wrap_socket(s, ...)  # 2. 통로를 암호화
```

## 요약

1. **TCP 연결**: 서버와 데이터를 주고받을 기본 통로 생성 (암호화 없음)
2. **SSL 핸드셰이크**: TCP 통로 위에서 암호화 설정 협상
3. **암호화 통신**: 이제 모든 데이터가 암호화되어 전송됨

## 핵심 포인트

- SSL 핸드셰이크는 TCP 연결 **이후**에 이루어짐
- TCP 연결 없이는 SSL 암호화를 할 수 없음
- `wrap_socket()`은 반드시 `connect()` 이후에 호출해야 함
