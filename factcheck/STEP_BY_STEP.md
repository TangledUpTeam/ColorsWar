# 단계별 실행 가이드 (API 키 불필요) 🚀

## 📌 요약
**OpenAI API 키 없이** 팩트체크 시스템을 실행하는 완전 가이드입니다.

---

## ✅ 실행 순서

### 1단계: 터미널 열기 (30초)

**macOS:**
- `Command + Space` → "Terminal" 입력 → Enter

**또는 VSCode에서:**
- `Ctrl + `` (백틱) → 터미널 열림

---

### 2단계: 프로젝트 폴더로 이동 (10초)

```bash
cd /Users/jinmokim/dev/ColorWar/factcheck
```

**확인:**
```bash
pwd
# 출력: /Users/jinmokim/dev/ColorWar/factcheck
```

---

### 3단계: 패키지 설치 (2-3분)

```bash
pip install -r requirements.txt
```

**또는 pip3:**
```bash
pip3 install -r requirements.txt
```

**설치되는 패키지:**
- `sentence-transformers` (문장 임베딩, ~500MB)
- `torch` (딥러닝 프레임워크, ~700MB)
- `rank-bm25` (검색 알고리즘)
- 기타 유틸리티

**예상 출력:**
```
Installing collected packages: torch, sentence-transformers, rank-bm25...
Successfully installed ...
```

---

### 4단계: 빠른 테스트 (30초-1분)

```bash
python quick_test.py
```

**첫 실행 시:**
- 임베딩 모델 자동 다운로드 (~500MB, 1-2분)
- 이후에는 캐시 사용 (즉시 실행)

**예상 출력:**
```
================================================================================
🧪 팩트체크 시스템 빠른 테스트 (API 키 불필요)
================================================================================

[1/4] 필요한 패키지 확인 중...
  ✓ PyTorch 설치됨
  ✓ sentence-transformers 설치됨
  ✓ rank-bm25 설치됨

[2/4] 데이터 파일 확인 중...
  ✓ mock_claims.json 존재
  ✓ mock_documents.json 존재

[3/4] 로컬 파이프라인 로드 중...
  📥 임베딩 모델 로드 중... (첫 실행 시 ~500MB 다운로드)
  ✓ 파이프라인 초기화 완료!

[4/4] 팩트체크 테스트 실행...
================================================================================
📋 주장: 대통령이 되면 수사 중단돼서 감옥 안 간다더라.
================================================================================
✅ 판정: True
⭐ 신뢰도: 7.2/10 (높음)
...
```

---

### 5단계: 실제 사용 (즉시)

#### 🔹 단일 팩트체크
```bash
python main_local.py --claim "대통령이 되면 수사 중단돼서 감옥 안 간다더라."
```

#### 🔹 다른 주장 테스트
```bash
python main_local.py --claim "탄소중립 기본법이 폐기됐는데 언론은 보도하지 않는다."
```

#### 🔹 10개 주장 일괄 처리
```bash
python main_local.py --batch data/mock_claims.json --output results.json
```

**결과 확인:**
```bash
cat results.json
```

---

## 🎯 완전한 실행 예시 (복사-붙여넣기)

```bash
# 1. 폴더 이동
cd /Users/jinmokim/dev/ColorWar/factcheck

# 2. 패키지 설치 (처음 한 번만)
pip install -r requirements.txt

# 3. 빠른 테스트
python quick_test.py

# 4. 단일 팩트체크
python main_local.py --claim "대통령이 되면 수사 중단돼서 감옥 안 간다더라."

# 5. 배치 처리
python main_local.py --batch data/mock_claims.json
```

---

## 📊 출력 예시

### 단일 팩트체크 결과:
```
================================================================================
📋 주장: 대통령이 되면 수사 중단돼서 감옥 안 간다더라.
================================================================================
✅ 판정: True
⭐ 신뢰도: 7.2/10 (높음)

💡 판정 근거:
   주장을 뒷받침하는 Evidence가 5개 발견되었습니다.

📚 참고 Evidence (5개):

   [1] 정부공식문서 (2024-01-15)
       헌법 제84조에 따르면 대통령은 재임 중 형사상 소추를 받지 않는다. 다만 대통령직을 사임하거나 퇴임한 ...
       관련도: 0.92

   [2] 법률신문 (2024-02-10)
       대통령이 퇴임하면 재임 중 중단됐던 수사가 재개될 수 있다...
       관련도: 0.88

📊 신뢰도 세부:
   - multiple_sources: 2.0
   - source_diversity: 2.0
   - recency: 1.0
   - matching_strength: 2.0
   - contradictions: 0.0
================================================================================
```

---

## 🔧 문제 해결

### ❌ "No module named 'torch'"
```bash
pip install torch
```

### ❌ "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### ❌ "Permission denied"
```bash
pip install --user -r requirements.txt
```

### ❌ 느린 다운로드 속도
첫 실행 시 ~500MB 모델 다운로드는 정상입니다.
캐시 위치: `~/.cache/huggingface/hub/`

### ❌ "ImportError: attempted relative import"
```bash
# 프로젝트 루트에서 실행하세요
cd /Users/jinmokim/dev/ColorWar/factcheck
python main_local.py --claim "테스트"
```

---

## 📁 파일 역할

| 파일 | 역할 | API 키 필요? |
|------|------|--------------|
| `main_local.py` | **메인 실행 파일 (로컬)** | ❌ 불필요 |
| `main.py` | 메인 실행 파일 (OpenAI) | ✅ 필요 |
| `quick_test.py` | 빠른 테스트 | ❌ 불필요 |
| `pipeline_local.py` | 로컬 파이프라인 | ❌ 불필요 |
| `models/judge_local.py` | 로컬 판정 시스템 | ❌ 불필요 |

---

## 🚀 다음 단계

1. ✅ **테스트 완료**
2. ✅ **단일 팩트체크 실행**
3. ✅ **배치 처리 실행**
4. 📝 **자신의 문서 추가**: `data/` 폴더에 JSON 추가
5. 🎨 **웹 UI 추가**: Flask/FastAPI로 API 서버 구축
6. 🤖 **정확도 향상**: Ollama 설치 후 `--method ollama` 사용

---

## 💡 핵심 명령어 요약

```bash
# API 키 없이 즉시 사용 가능!
python main_local.py --claim "당신의 주장"

# 배치 처리
python main_local.py --batch data/mock_claims.json

# 빠른 테스트
python quick_test.py
```

---

## 🎯 정리

| 단계 | 명령어 | 시간 |
|------|--------|------|
| 1. 폴더 이동 | `cd factcheck` | 10초 |
| 2. 패키지 설치 | `pip install -r requirements.txt` | 2-3분 |
| 3. 테스트 | `python quick_test.py` | 30초-1분 |
| 4. 실행 | `python main_local.py --claim "..."` | 즉시 |

**총 소요 시간: 약 5분** (패키지 설치 포함)

---

질문이 있으시면 언제든지 물어보세요! 🙋‍♂️

