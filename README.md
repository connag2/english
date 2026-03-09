# English Vocab App (Desktop)

간단하고 가벼운 데스크톱 영단어 암기 프로그램입니다.

## 실행
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

## 핵심 기능
- 단어 입력 3가지: 직접 입력 / 여러 줄 입력 / txt 파일 불러오기
- 입력 문법: `word=meaning1|meaning2|meaning3`
- 저장 전 미리보기, 오류 줄 표시, 중복 단어 뜻 병합
- 단어장 검색/수정/삭제/정렬
- 학습(영어→뜻), 복습(객관식), 오답 재시험
- JSON 저장 + 기본 복습 주기(level 기반)
