import os
import json
import csv
from datetime import datetime, date
from flask import (
    Flask, render_template, request, redirect,
    url_for, send_from_directory, jsonify, session, Response
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "narae2025secret")
app.jinja_env.filters['enumerate'] = enumerate

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
SHARE_DIR   = os.path.join(BASE_DIR, "shared")
DATA_DIR    = os.path.join(BASE_DIR, "data")
ALLOWED_EXT = {"pdf","hwp","hwpx","docx","xlsx","pptx","jpg","jpeg","png","gif","mp4","mp3","txt","zip"}
STUDENT_COUNT = 22
TEACHER_PW    = os.environ.get("TEACHER_PW", "narae1234")

for d in [UPLOAD_DIR, SHARE_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# ── 헬퍼 ──────────────────────────────────────────
def allowed(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def passwords_path():
    return os.path.join(DATA_DIR, "passwords.json")

def attendance_path(d=None):
    d = d or date.today().isoformat()
    return os.path.join(DATA_DIR, f"attendance_{d}.json")

def notices_path():
    return os.path.join(DATA_DIR, "notices.json")

def quiz_path():
    return os.path.join(DATA_DIR, "quizzes.json")

def quiz_answers_path(quiz_id):
    return os.path.join(DATA_DIR, f"answers_{quiz_id}.json")

def exams_path():
    return os.path.join(DATA_DIR, "exams.json")

def exam_answers_path(exam_id):
    return os.path.join(DATA_DIR, f"exam_answers_{exam_id}.json")

def is_teacher():
    return session.get("role") == "teacher"

def get_student_num():
    return session.get("student_num")

def today_str():
    return date.today().strftime("%Y년 %m월 %d일")

def record_attendance(num):
    att = load_json(attendance_path(), {})
    key = str(num)
    if key not in att:
        att[key] = datetime.now().strftime("%H:%M:%S")
        save_json(attendance_path(), att)

def get_all_attendance_dates():
    dates = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.startswith("attendance_") and fname.endswith(".json"):
            d = fname.replace("attendance_","").replace(".json","")
            dates.append(d)
    return dates

# ── 로그인 ─────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", student_count=STUDENT_COUNT)

@app.route("/login", methods=["POST"])
def login():
    role = request.form.get("role")

    if role == "teacher":
        if request.form.get("password","") == TEACHER_PW:
            session["role"] = "teacher"
            return redirect(url_for("teacher_dashboard"))
        return render_template("index.html", student_count=STUDENT_COUNT, error="비밀번호가 틀렸어요.")

    elif role == "student":
        try:
            num = int(request.form.get("student_num",""))
            pw  = request.form.get("password","").strip()
            if not (1 <= num <= STUDENT_COUNT):
                raise ValueError
        except:
            return render_template("index.html", student_count=STUDENT_COUNT, error="번호를 확인해주세요.")

        passwords = load_json(passwords_path(), {})
        key = str(num)

        # 비밀번호 미등록 → 등록 화면
        if key not in passwords:
            if pw == "":
                return render_template("register.html", num=num)
            # 등록 처리
            if len(pw) == 4 and pw.isdigit():
                passwords[key] = pw
                save_json(passwords_path(), passwords)
                session["role"] = "student"
                session["student_num"] = num
                record_attendance(num)
                return redirect(url_for("student_dashboard"))
            return render_template("register.html", num=num, error="숫자 4자리로 입력해주세요.")

        # 등록된 경우 → 비밀번호 확인
        if pw == "":
            return render_template("index.html", student_count=STUDENT_COUNT,
                                   need_pw=num)
        if passwords[key] == pw:
            session["role"] = "student"
            session["student_num"] = num
            record_attendance(num)
            return redirect(url_for("student_dashboard"))
        return render_template("index.html", student_count=STUDENT_COUNT,
                               error="비밀번호가 틀렸어요.", need_pw=num)

    return redirect(url_for("index"))

@app.route("/register", methods=["POST"])
def register():
    num = request.form.get("num","")
    pw  = request.form.get("new_pw","").strip()
    try:
        num = int(num)
        if not (1 <= num <= STUDENT_COUNT): raise ValueError
    except:
        return redirect(url_for("index"))
    if len(pw) != 4 or not pw.isdigit():
        return render_template("register.html", num=num, error="숫자 4자리로 입력해주세요.")
    passwords = load_json(passwords_path(), {})
    passwords[str(num)] = pw
    save_json(passwords_path(), passwords)
    session["role"] = "student"
    session["student_num"] = num
    record_attendance(num)
    return redirect(url_for("student_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ── 학생 대시보드 ───────────────────────────────────
@app.route("/student")
def student_dashboard():
    num = get_student_num()
    if not num:
        return redirect(url_for("index"))
    notices        = load_json(notices_path(), [])
    quizzes        = load_json(quiz_path(), [])
    active_quizzes = [q for q in quizzes if q.get("active")]
    exams          = load_json(exams_path(), [])
    active_exams   = [e for e in exams if e.get("active")]
    shared_files   = sorted(os.listdir(SHARE_DIR)) if os.path.exists(SHARE_DIR) else []
    # 이미 제출한 시험
    submitted_exams = set()
    for e in exams:
        ans = load_json(exam_answers_path(e["id"]), {})
        if str(num) in ans:
            submitted_exams.add(e["id"])
    return render_template("student.html",
        num=num, notices=notices,
        active_quizzes=active_quizzes,
        active_exams=active_exams,
        submitted_exams=submitted_exams,
        shared_files=shared_files,
        today=today_str())

# ── 파일 업로드 ────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload_file():
    num = get_student_num()
    if not num:
        return jsonify({"ok": False, "msg": "로그인 필요"})
    if "file" not in request.files:
        return jsonify({"ok": False, "msg": "파일이 없어요"})
    f = request.files["file"]
    if not f.filename or not allowed(f.filename):
        return jsonify({"ok": False, "msg": "파일을 확인해주세요"})
    ts   = datetime.now().strftime("%H%M%S")
    safe = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_DIR, f"{num}번_{ts}_{safe}"))
    return jsonify({"ok": True, "msg": f"'{f.filename}' 제출 완료!"})

@app.route("/download/<filename>")
def download_shared(filename):
    if not get_student_num() and not is_teacher():
        return redirect(url_for("index"))
    return send_from_directory(SHARE_DIR, filename, as_attachment=True)

# ── 퀴즈 제출 ──────────────────────────────────────
@app.route("/quiz/<quiz_id>/submit", methods=["POST"])
def quiz_submit(quiz_id):
    num = get_student_num()
    if not num:
        return jsonify({"ok": False, "msg": "로그인 필요"})
    answers = load_json(quiz_answers_path(quiz_id), {})
    if str(num) in answers:
        return jsonify({"ok": False, "msg": "이미 제출했어요!"})
    data = request.get_json()
    answers[str(num)] = {"answers": data.get("answers", {}), "submitted_at": datetime.now().strftime("%H:%M:%S")}
    save_json(quiz_answers_path(quiz_id), answers)
    return jsonify({"ok": True, "msg": "제출 완료!"})

# ── 시험 제출 + 자동채점 ────────────────────────────
@app.route("/exam/<exam_id>/submit", methods=["POST"])
def exam_submit(exam_id):
    num = get_student_num()
    if not num:
        return jsonify({"ok": False, "msg": "로그인 필요"})
    exams = load_json(exams_path(), [])
    exam  = next((e for e in exams if e["id"] == exam_id), None)
    if not exam:
        return jsonify({"ok": False, "msg": "시험을 찾을 수 없어요"})
    all_answers = load_json(exam_answers_path(exam_id), {})
    if str(num) in all_answers:
        return jsonify({"ok": False, "msg": "이미 제출했어요!"})
    data    = request.get_json()
    student_answers = data.get("answers", {})
    answer_key = exam.get("answer_key", {})

    # 채점
    score   = 0
    total_q = exam.get("question_count", 20)
    results = {}
    per_q   = 100 / total_q if total_q else 5

    for i in range(1, total_q + 1):
        key      = str(i)
        student  = student_answers.get(key, "").strip()
        correct  = str(answer_key.get(key, "")).strip()
        is_right = (student == correct) if correct else None
        results[key] = {"student": student, "correct": correct, "is_right": is_right}
        if is_right:
            score += per_q

    score = round(score)
    all_answers[str(num)] = {
        "answers": student_answers,
        "results": results,
        "score": score,
        "submitted_at": datetime.now().strftime("%H:%M:%S"),
        "date": date.today().isoformat()
    }
    save_json(exam_answers_path(exam_id), all_answers)
    return jsonify({"ok": True, "msg": f"제출 완료! 점수: {score}점", "score": score, "results": results})

# ══════════════════════════════════════════════════
# 선생님 대시보드
# ══════════════════════════════════════════════════
@app.route("/teacher")
def teacher_dashboard():
    if not is_teacher():
        return redirect(url_for("index"))
    att          = load_json(attendance_path(), {})
    notices      = load_json(notices_path(), [])
    quizzes      = load_json(quiz_path(), [])
    exams        = load_json(exams_path(), [])
    shared_files = sorted(os.listdir(SHARE_DIR))
    uploads      = sorted(os.listdir(UPLOAD_DIR))
    checked = sorted([int(k) for k in att.keys()])
    absent  = [n for n in range(1, STUDENT_COUNT+1) if n not in checked]
    for q in quizzes:
        q["submit_count"] = len(load_json(quiz_answers_path(q["id"]), {}))
    for e in exams:
        ans = load_json(exam_answers_path(e["id"]), {})
        e["submit_count"] = len(ans)
        scores = [v["score"] for v in ans.values() if "score" in v]
        e["avg_score"] = round(sum(scores)/len(scores)) if scores else "-"
    passwords = load_json(passwords_path(), {})
    registered = [int(k) for k in passwords.keys()]
    return render_template("teacher.html",
        att=att, checked=checked, absent=absent,
        notices=notices, quizzes=quizzes, exams=exams,
        shared_files=shared_files, uploads=uploads,
        today=today_str(), total=STUDENT_COUNT,
        registered=registered)

# ── 학생별 상세 페이지 ──────────────────────────────
@app.route("/teacher/student/<int:num>")
def student_detail(num):
    if not is_teacher():
        return redirect(url_for("index"))
    if not (1 <= num <= STUDENT_COUNT):
        return redirect(url_for("teacher_dashboard"))

    # 출결 현황 (전체 날짜)
    att_dates = get_all_attendance_dates()
    att_records = {}
    for d in att_dates:
        att = load_json(attendance_path(d), {})
        att_records[d] = {"present": str(num) in att, "time": att.get(str(num), "")}

    # 과제 제출 현황
    uploads = [f for f in sorted(os.listdir(UPLOAD_DIR)) if f.startswith(f"{num}번_")]

    # 퀴즈 응답
    quizzes = load_json(quiz_path(), [])
    quiz_records = []
    for q in quizzes:
        ans = load_json(quiz_answers_path(q["id"]), {})
        if str(num) in ans:
            quiz_records.append({"title": q["title"], "data": ans[str(num)], "questions": q["questions"]})

    # 시험 점수
    exams = load_json(exams_path(), [])
    exam_records = []
    for e in exams:
        ans = load_json(exam_answers_path(e["id"]), {})
        if str(num) in ans:
            exam_records.append({"title": e["title"], "data": ans[str(num)]})

    present_count = sum(1 for v in att_records.values() if v["present"])
    total_days    = len(att_dates)

    return render_template("student_detail.html",
        num=num, att_records=att_records,
        present_count=present_count, total_days=total_days,
        uploads=uploads, quiz_records=quiz_records,
        exam_records=exam_records)

# ── 공지 ───────────────────────────────────────────
@app.route("/teacher/notice/add", methods=["POST"])
def notice_add():
    if not is_teacher(): return redirect(url_for("index"))
    notices = load_json(notices_path(), [])
    content = request.form.get("content","").strip()
    if content:
        notices.insert(0, {"id": datetime.now().strftime("%Y%m%d%H%M%S"),
                           "content": content, "date": datetime.now().strftime("%m/%d %H:%M")})
        save_json(notices_path(), notices)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/notice/delete/<nid>")
def notice_delete(nid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(notices_path(), [n for n in load_json(notices_path(), []) if n["id"] != nid])
    return redirect(url_for("teacher_dashboard"))

# ── 파일 배포 ──────────────────────────────────────
@app.route("/teacher/share", methods=["POST"])
def teacher_share():
    if not is_teacher(): return redirect(url_for("teacher_dashboard"))
    f = request.files.get("file")
    if f and f.filename and allowed(f.filename):
        f.save(os.path.join(SHARE_DIR, secure_filename(f.filename)))
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/share/delete/<filename>")
def teacher_share_delete(filename):
    if not is_teacher(): return redirect(url_for("index"))
    path = os.path.join(SHARE_DIR, secure_filename(filename))
    if os.path.exists(path): os.remove(path)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/uploads/<filename>")
def teacher_download_upload(filename):
    if not is_teacher(): return redirect(url_for("index"))
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route("/teacher/uploads/delete/<filename>")
def teacher_delete_upload(filename):
    if not is_teacher(): return redirect(url_for("index"))
    path = os.path.join(UPLOAD_DIR, secure_filename(filename))
    if os.path.exists(path): os.remove(path)
    return redirect(url_for("teacher_dashboard"))

# ── 출석 CSV ───────────────────────────────────────
@app.route("/teacher/attendance/export")
def export_attendance():
    if not is_teacher(): return redirect(url_for("index"))
    att = load_json(attendance_path(), {})
    from io import StringIO
    si = StringIO()
    w  = csv.writer(si)
    w.writerow(["번호","출석","시각"])
    for n in range(1, STUDENT_COUNT+1):
        key = str(n)
        w.writerow([f"{n}번", "출석" if key in att else "결석", att.get(key,"")])
    return Response("\ufeff"+si.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=출석_{date.today()}.csv"})

# ── 퀴즈 ───────────────────────────────────────────
@app.route("/teacher/quiz/add", methods=["POST"])
def quiz_add():
    if not is_teacher(): return redirect(url_for("index"))
    quizzes = load_json(quiz_path(), [])
    title   = request.form.get("title","").strip()
    qtype   = request.form.get("qtype","survey")
    questions_raw = request.form.get("questions","").strip()
    if title and questions_raw:
        qs = []
        for line in questions_raw.split("\n"):
            line = line.strip()
            if not line: continue
            if "|" in line:
                q_text, choices_raw = line.split("|",1)
                qs.append({"text": q_text.strip(), "type": "choice",
                           "choices": [c.strip() for c in choices_raw.split(",") if c.strip()]})
            else:
                qs.append({"text": line, "type": "text"})
        if qs:
            qid = datetime.now().strftime("%Y%m%d%H%M%S")
            quizzes.append({"id": qid, "title": title, "qtype": qtype, "questions": qs,
                            "active": True, "created": datetime.now().strftime("%m/%d %H:%M")})
            save_json(quiz_path(), quizzes)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/toggle/<qid>")
def quiz_toggle(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quizzes = load_json(quiz_path(), [])
    for q in quizzes:
        if q["id"] == qid: q["active"] = not q.get("active", True)
    save_json(quiz_path(), quizzes)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/delete/<qid>")
def quiz_delete(qid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(quiz_path(), [q for q in load_json(quiz_path(), []) if q["id"] != qid])
    ans = quiz_answers_path(qid)
    if os.path.exists(ans): os.remove(ans)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/<qid>/results")
def quiz_results(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quiz = next((q for q in load_json(quiz_path(), []) if q["id"] == qid), None)
    if not quiz: return redirect(url_for("teacher_dashboard"))
    return render_template("quiz_results.html",
        quiz=quiz, answers=load_json(quiz_answers_path(qid), {}), total=STUDENT_COUNT)

# ── 시험 만들기 ────────────────────────────────────
@app.route("/teacher/exam/add", methods=["POST"])
def exam_add():
    if not is_teacher(): return redirect(url_for("index"))
    exams  = load_json(exams_path(), [])
    title  = request.form.get("title","").strip()
    q_count = int(request.form.get("question_count", 20))
    # 정답 파싱: "1:3,2:1,3:4,..." 또는 textarea 한 줄씩
    answer_raw = request.form.get("answer_key","").strip()
    answer_key = {}
    for item in answer_raw.replace("\n",",").split(","):
        item = item.strip()
        if ":" in item:
            qn, ans = item.split(":",1)
            answer_key[qn.strip()] = ans.strip()
    if title:
        eid = datetime.now().strftime("%Y%m%d%H%M%S")
        exams.append({"id": eid, "title": title, "question_count": q_count,
                      "answer_key": answer_key, "active": True,
                      "created": datetime.now().strftime("%m/%d %H:%M")})
        save_json(exams_path(), exams)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/toggle/<eid>")
def exam_toggle(eid):
    if not is_teacher(): return redirect(url_for("index"))
    exams = load_json(exams_path(), [])
    for e in exams:
        if e["id"] == eid: e["active"] = not e.get("active", True)
    save_json(exams_path(), exams)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/delete/<eid>")
def exam_delete(eid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(exams_path(), [e for e in load_json(exams_path(), []) if e["id"] != eid])
    ans = exam_answers_path(eid)
    if os.path.exists(ans): os.remove(ans)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/<eid>/results")
def exam_results(eid):
    if not is_teacher(): return redirect(url_for("index"))
    exam = next((e for e in load_json(exams_path(), []) if e["id"] == eid), None)
    if not exam: return redirect(url_for("teacher_dashboard"))
    return render_template("exam_results.html",
        exam=exam, answers=load_json(exam_answers_path(eid), {}), total=STUDENT_COUNT)

# ── 학생 비밀번호 초기화 (선생님) ──────────────────
@app.route("/teacher/reset_pw/<int:num>")
def reset_student_pw(num):
    if not is_teacher(): return redirect(url_for("index"))
    passwords = load_json(passwords_path(), {})
    passwords.pop(str(num), None)
    save_json(passwords_path(), passwords)
    return redirect(url_for("teacher_dashboard"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
