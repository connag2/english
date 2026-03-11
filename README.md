# VocaFlow Web

PySide6 데스크톱 앱 대신, **Flask 기반 웹앱**으로 전환한 영단어 암기 도구입니다.
핸드폰/PC 브라우저에서 같은 UI를 사용할 수 있습니다.

## 실행
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

브라우저에서 접속:
- `http://localhost:5000`

## 핵심 기능
- 단어 입력 3가지: 직접 입력 / 여러 줄 입력 / txt 파일 업로드
- 입력 문법: `word=meaning1|meaning2|meaning3`
- 저장 전 미리보기, 오류 줄 표시, 중복 단어 뜻 자동 병합
- 단어장 검색/수정/삭제/정렬(알파벳/최근/오답 많은 순)
- 학습 모드: 영어→뜻, 객관식
- 오답만 다시 풀기
- JSON 저장 + 간단 SRS 스케줄
- 모바일 반응형 UI(Tailwind CDN)

## 파일 구조
- `app.py`: Flask 라우트/학습 세션 로직
- `templates/`: 화면 템플릿(`index`, `wordbook`, `study`, `result`)
- `models.py`, `storage.py`, `word_manager.py`, `study_engine.py`: 핵심 로직/저장
