# Uvicorn 실행 가이드

## 🚀 기본 실행

### 가장 간단한 방법

```bash
uvicorn app_battle:app
```

기본값:
- Host: 127.0.0.1 (로컬호스트만)
- Port: 8000
- 자동 재시작: 비활성화

### 권장 방법 (개발용)

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --reload
```

- `--host 0.0.0.0`: 외부 접속 허용
- `--port 5000`: 포트 5000 사용
- `--reload`: 코드 변경 시 자동 재시작

## 📋 주요 옵션

### 기본 옵션

```bash
# 호스트 설정
uvicorn app_battle:app --host 0.0.0.0    # 모든 IP에서 접속 가능
uvicorn app_battle:app --host 127.0.0.1  # 로컬에서만 접속

# 포트 설정
uvicorn app_battle:app --port 5000       # 5000 포트 사용
uvicorn app_battle:app --port 8080       # 8080 포트 사용

# 자동 재시작 (개발용)
uvicorn app_battle:app --reload          # 코드 변경 시 자동 재시작
```

### 성능 옵션

```bash
# 워커 수 설정 (운영용)
uvicorn app_battle:app --workers 4       # 4개 워커 프로세스

# 로그 레벨
uvicorn app_battle:app --log-level info     # 기본
uvicorn app_battle:app --log-level debug    # 디버그
uvicorn app_battle:app --log-level warning  # 경고만
```

### 고급 옵션

```bash
# SSL/HTTPS
uvicorn app_battle:app --ssl-keyfile key.pem --ssl-certfile cert.pem

# 접속 제한
uvicorn app_battle:app --limit-concurrency 100

# 타임아웃
uvicorn app_battle:app --timeout-keep-alive 5
```

## 🎯 시나리오별 명령어

### 로컬 개발

```bash
uvicorn app_battle:app --reload
```

### 팀 공유 (같은 네트워크)

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --reload
```

### 운영 환경 (단일 서버)

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --workers 4
```

### 백그라운드 실행

```bash
# Linux/Mac
uvicorn app_battle:app --host 0.0.0.0 --port 5000 &

# nohup으로 실행 (로그아웃 후에도 유지)
nohup uvicorn app_battle:app --host 0.0.0.0 --port 5000 > server.log 2>&1 &

# Windows (PowerShell)
Start-Process -NoNewWindow uvicorn -ArgumentList "app_battle:app --host 0.0.0.0 --port 5000"
```

### 특정 IP만 허용

```bash
# 방화벽이나 프록시 사용 권장
# 애플리케이션 레벨에서는 FastAPI의 미들웨어로 처리
```

## 🔧 문제 해결

### 포트가 이미 사용 중

```bash
# 다른 포트 사용
uvicorn app_battle:app --port 8000

# 또는 기존 프로세스 종료
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### 자동 재시작이 작동하지 않음

```bash
# watchfiles 설치
pip install watchfiles

# 다시 실행
uvicorn app_battle:app --reload
```

### 외부에서 접속 안됨

```bash
# 0.0.0.0으로 바인딩 확인
uvicorn app_battle:app --host 0.0.0.0 --port 5000

# 방화벽 확인
# Windows: 방화벽 설정에서 5000 포트 허용
# Linux: sudo ufw allow 5000
```

## 📊 성능 비교

| 방법 | 속도 | 개발 편의성 | 운영 적합성 |
|------|------|-------------|-------------|
| `python app_battle.py` | ⚡⚡ | ⭐⭐⭐ | ⭐ |
| `uvicorn --reload` | ⚡⚡ | ⭐⭐⭐ | ⭐ |
| `uvicorn --workers 4` | ⚡⚡⚡ | ⭐ | ⭐⭐⭐ |

## 💡 추천 설정

### 개발 중

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --reload --log-level debug
```

### 테스트

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --workers 2
```

### 운영 (소규모)

```bash
uvicorn app_battle:app --host 0.0.0.0 --port 5000 --workers 4 --log-level warning
```

## 🔄 프로세스 관리

### systemd (Linux)

`/etc/systemd/system/battle.service`:

```ini
[Unit]
Description=AI Persona Battle System
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/test
ExecStart=/usr/bin/uvicorn app_battle:app --host 0.0.0.0 --port 5000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

실행:

```bash
sudo systemctl enable battle
sudo systemctl start battle
sudo systemctl status battle
```

### PM2 (Node.js 도구지만 Python도 지원)

```bash
# PM2 설치
npm install -g pm2

# 실행
pm2 start "uvicorn app_battle:app --host 0.0.0.0 --port 5000" --name battle

# 관리
pm2 status
pm2 logs battle
pm2 restart battle
pm2 stop battle
```

## 📚 더 알아보기

공식 문서: https://www.uvicorn.org/

---

**Uvicorn으로 빠르고 안정적인 서버를 운영하세요! 🚀**

