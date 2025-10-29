# XXXX

간단한 Python 프로젝트 골격입니다.

## 프로젝트 구조

```text
C:\dev\XXXX\
  ├─ .venv\              ← 가상환경(커밋 금지)
  ├─ src\                ← 코드
  │   └─ main.py
  ├─ requirements.txt
  └─ README.md
```

## 준비 (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

만약 실행 정책으로 인해 활성화가 막히면 다음을 관리자 권한 PowerShell에서 한 번 실행하세요.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 실행

```powershell
python .\src\main.py
```

## 배포/패키징 (선택)
- 추가 라이브러리가 필요하면 `requirements.txt`에 패키지를 추가하고 `pip install -r requirements.txt`로 설치하세요.


