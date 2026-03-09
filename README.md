# English Vocab App (Desktop)

간단하고 가벼운 데스크톱 영단어 암기 프로그램입니다.

## 빠른 실행 (개발 모드)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

또는:
```bash
python3 main.py
```

## EXE 만들기 (Windows, 권장)
`build_exe.bat`는 아래를 자동으로 수행합니다.
- Python 런처 자동 탐지(`py -3` / `python`)
- `.venv` 자동 생성
- 의존성 자동 설치 (`requirements.txt`)
- PyInstaller onefile 빌드
- 결과물: `dist\VocaFlow.exe`

실행:
```bat
build_exe.bat
```

## EXE 빌드 실패 시 체크
1. Python 3.10+ 설치 여부
2. 회사/학교 프록시 환경에서 pip 차단 여부
3. 백신이 `dist\VocaFlow.exe` 생성 차단 여부

## 빌드 스크립트
- `build_exe.bat`: Windows 원클릭 EXE 빌드(자동 venv/의존성 설치 포함)
- `build_exe.sh`: 현재 OS용 PyInstaller 빌드(Windows에서 실행 시 `.exe` 생성)

## 핵심 기능
- 단어 입력 3가지: 직접 입력 / 여러 줄 입력 / txt 파일 불러오기
- 입력 문법: `word=meaning1|meaning2|meaning3`
- 저장 전 미리보기, 오류 줄 표시, 중복 단어 뜻 병합
- 단어장 검색/수정/삭제/정렬
- 학습(영어→뜻), 복습(객관식), 오답 재시험
- JSON 저장 + 기본 복습 주기(level 기반)
- 학습 진행 중 정답 처리 시 즉시 저장(갑작스런 종료 대비)
- 일일 통계(`오늘 학습`)는 날짜가 바뀌면 자동 리셋


## BAT 실행이 계속 실패할 때
- `build_exe.bat`는 실패 시 창이 닫히지 않고 `pause` 상태로 멈춥니다.
- 상세 원인은 루트의 `build_exe.log`를 확인하세요.
- 프록시/사내망 환경이면 pip 다운로드가 막힐 수 있습니다.
