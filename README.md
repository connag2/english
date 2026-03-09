# English Vocab App (Desktop)

간단하고 가벼운 데스크톱 영단어 암기 프로그램입니다.

## 빠른 실행
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

## EXE 만들기 (Windows)
Windows에서 아래 순서로 실행하면 `.exe`를 만들 수 있습니다.

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
build_exe.bat
```

생성 위치(환경에 따라 둘 중 하나):
- `dist\VocaFlow.exe`
- `dist\VocaFlow\VocaFlow.exe`

## 빌드 스크립트
- `build_exe.bat`: Windows `.exe` 빌드용
- `build_exe.sh`: 현재 OS용 PyInstaller 빌드(Windows에서 실행하면 `.exe` 생성)

## 핵심 기능
- 단어 입력 3가지: 직접 입력 / 여러 줄 입력 / txt 파일 불러오기
- 입력 문법: `word=meaning1|meaning2|meaning3`
- 저장 전 미리보기, 오류 줄 표시, 중복 단어 뜻 병합
- 단어장 검색/수정/삭제/정렬
- 학습(영어→뜻), 복습(객관식), 오답 재시험
- JSON 저장 + 기본 복습 주기(level 기반)
