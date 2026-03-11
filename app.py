from __future__ import annotations

import random
from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

from models import AppStats
from storage import Storage
from study_engine import StudyEngine
from word_manager import ParseResult, WordManager

app = Flask(__name__)
app.secret_key = "vocaflow-dev-secret"

storage = Storage("data/words.json")


def get_manager() -> WordManager:
    return WordManager(storage)


def load_stats() -> AppStats:
    return storage.load_stats()


def save_all(manager: WordManager, stats: AppStats) -> None:
    storage.save_words(manager.all_words(), stats)


def due_count(words) -> int:
    today = date.today().isoformat()
    return len([w for w in words if not w.next_review or w.next_review <= today])


@app.get("/")
def index():
    manager = get_manager()
    stats = load_stats()
    words = manager.all_words()
    preview = session.get("bulk_preview", {})
    return render_template(
        "index.html",
        total=len(words),
        due=due_count(words),
        today_studied=stats.today_studied,
        recent_wrong=stats.recent_wrong_words,
        preview_items=preview.get("items", []),
        preview_errors=preview.get("errors", []),
    )


@app.post("/add-single")
def add_single():
    manager = get_manager()
    err = manager.add_single(request.form.get("word", ""), request.form.get("meanings", ""))
    if err:
        flash(err, "error")
    else:
        flash("단어가 추가되었습니다.", "ok")
    return redirect(url_for("index"))


@app.post("/bulk-preview")
def bulk_preview():
    manager = get_manager()
    parsed = manager.parse_bulk(request.form.get("bulk_text", ""))
    items = [f"{w} = {' | '.join(sorted(m))}" for w, m in sorted(parsed.merged.items())]
    session["bulk_preview"] = {"items": items, "errors": parsed.errors, "raw": request.form.get("bulk_text", "")}
    return redirect(url_for("index"))


@app.post("/bulk-save")
def bulk_save():
    manager = get_manager()
    payload = session.get("bulk_preview")
    if not payload:
        flash("먼저 미리보기를 실행해주세요.", "error")
        return redirect(url_for("index"))

    parsed = manager.parse_bulk(payload.get("raw", ""))
    if not parsed.merged:
        flash("저장할 유효 단어가 없습니다.", "error")
        return redirect(url_for("index"))

    manager.apply_parse_result(parsed)
    session.pop("bulk_preview", None)
    flash("여러 줄 단어가 저장되었습니다.", "ok")
    return redirect(url_for("index"))


@app.post("/upload-preview")
def upload_preview():
    manager = get_manager()
    file = request.files.get("txt_file")
    if not file or not file.filename:
        flash("파일을 선택해주세요.", "error")
        return redirect(url_for("index"))

    data = file.read()
    text = None
    for enc in ("utf-8-sig", "cp949"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        flash("파일 인코딩을 읽을 수 없습니다.", "error")
        return redirect(url_for("index"))

    parsed = manager.parse_bulk(text)
    items = [f"{w} = {' | '.join(sorted(m))}" for w, m in sorted(parsed.merged.items())]
    session["bulk_preview"] = {"items": items, "errors": parsed.errors, "raw": text}
    flash("파일 미리보기를 불러왔습니다.", "ok")
    return redirect(url_for("index"))


@app.get("/wordbook")
def wordbook():
    manager = get_manager()
    q = request.args.get("q", "").strip().lower()
    sort_key = request.args.get("sort", "alpha")
    words = manager.all_words()
    if sort_key == "recent":
        words.sort(key=lambda w: w.created_at, reverse=True)
    elif sort_key == "wrong":
        words.sort(key=lambda w: w.wrong, reverse=True)
    else:
        words.sort(key=lambda w: w.word)

    if q:
        words = [w for w in words if q in w.word or any(q in m for m in w.meanings)]

    return render_template("wordbook.html", words=words, q=q, sort_key=sort_key)


@app.post("/word/update")
def word_update():
    manager = get_manager()
    old_word = request.form.get("old_word", "")
    new_word = request.form.get("new_word", "")
    meanings = [m.strip() for m in request.form.get("meanings", "").split("|")]
    err = manager.upsert_word(old_word, new_word, meanings)
    if err:
        flash(err, "error")
    else:
        flash("단어가 수정되었습니다.", "ok")
    return redirect(url_for("wordbook"))


@app.post("/word/delete")
def word_delete():
    manager = get_manager()
    manager.delete_word(request.form.get("word", ""))
    flash("단어가 삭제되었습니다.", "ok")
    return redirect(url_for("wordbook"))


@app.post("/study/start")
def study_start():
    mode = request.form.get("mode", "meaning")
    review_only = request.form.get("review_only") == "1"
    manager = get_manager()
    engine = StudyEngine(manager.all_words())
    pool = engine.select_words(review_only=review_only, limit=30)
    if not pool:
        flash("출제할 단어가 없습니다.", "error")
        return redirect(url_for("index"))

    questions = []
    for w in pool:
        q = engine.build_question(w, mode, pool)
        questions.append({"word": q.word.word, "prompt": q.prompt, "answer": q.answer, "choices": q.choices or []})

    session["study"] = {
        "mode": mode,
        "index": 0,
        "correct": 0,
        "answered": False,
        "wrong_words": [],
        "questions": questions,
    }
    return redirect(url_for("study"))


@app.get("/study")
def study():
    st = session.get("study")
    if not st:
        return redirect(url_for("index"))
    q = st["questions"][st["index"]]
    return render_template("study.html", st=st, q=q)


@app.post("/study/answer")
def study_answer():
    st = session.get("study")
    if not st:
        return redirect(url_for("index"))
    if st.get("answered"):
        return redirect(url_for("study"))

    manager = get_manager()
    stats = load_stats()
    q = st["questions"][st["index"]]
    entry = manager.words.get(q["word"])
    if not entry:
        flash("단어 데이터를 찾을 수 없습니다.", "error")
        return redirect(url_for("study"))

    mode = st["mode"]
    is_correct = False
    if mode == "mcq":
        selected = request.form.get("choice", "")
        if not selected:
            flash("보기를 선택해주세요.", "error")
            return redirect(url_for("study"))
        is_correct = selected == q["answer"]
    else:
        guess = request.form.get("guess", "").strip()
        is_correct = bool(guess and guess in entry.meanings)

    engine = StudyEngine(manager.all_words())
    engine.mark_result(entry, is_correct)

    stats.mark_studied()
    if is_correct:
        st["correct"] += 1
        flash("정답입니다!", "ok")
    else:
        st["wrong_words"].append(entry.word)
        stats.mark_wrong(entry.word)
        flash(f"오답입니다. 정답: {q['answer']}", "error")

    st["answered"] = True
    session["study"] = st
    save_all(manager, stats)
    return redirect(url_for("study"))


@app.post("/study/next")
def study_next():
    st = session.get("study")
    if not st:
        return redirect(url_for("index"))
    if not st.get("answered"):
        flash("정답 확인 후 다음으로 이동하세요.", "error")
        return redirect(url_for("study"))

    if st["index"] >= len(st["questions"]) - 1:
        session["result"] = {
            "total": len(st["questions"]),
            "correct": st["correct"],
            "wrong": len(st["questions"]) - st["correct"],
            "wrong_words": st["wrong_words"],
        }
        session.pop("study", None)
        return redirect(url_for("result"))

    st["index"] += 1
    st["answered"] = False
    session["study"] = st
    return redirect(url_for("study"))


@app.post("/study/quit")
def study_quit():
    st = session.get("study")
    if not st:
        return redirect(url_for("index"))
    answered_total = st["index"] + (1 if st.get("answered") else 0)
    session["result"] = {
        "total": answered_total,
        "correct": st["correct"],
        "wrong": max(0, answered_total - st["correct"]),
        "wrong_words": st["wrong_words"],
    }
    session.pop("study", None)
    return redirect(url_for("result"))


@app.get("/result")
def result():
    result_data = session.get("result")
    if not result_data:
        return redirect(url_for("index"))
    return render_template("result.html", result=result_data)


@app.post("/study/retry-wrong")
def retry_wrong():
    result_data = session.get("result")
    if not result_data:
        return redirect(url_for("index"))
    wrong_words = set(result_data.get("wrong_words", []))
    manager = get_manager()
    pool = [w for w in manager.all_words() if w.word in wrong_words]
    if not pool:
        flash("오답 단어가 없습니다.", "error")
        return redirect(url_for("index"))

    engine = StudyEngine(pool)
    selected = engine.select_words(review_only=False, limit=30)
    questions = []
    for w in selected:
        q = engine.build_question(w, "mcq", selected)
        questions.append({"word": q.word.word, "prompt": q.prompt, "answer": q.answer, "choices": q.choices or []})

    session["study"] = {"mode": "mcq", "index": 0, "correct": 0, "answered": False, "wrong_words": [], "questions": questions}
    return redirect(url_for("study"))


@app.post('/result/close')
def result_close():
    session.pop("result", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
