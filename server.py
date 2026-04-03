import os
import json
import csv
import socket
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
ALLOWED_EXT = {
    "pdf","hwp","hwpx","docx","xlsx","pptx",
    "jpg","jpeg","png","gif","mp4","mp3","txt","zip"
}
STUDENT_COUNT = 22
TEACHER_PW    = os.environ.get("TEACHER_PW", "narae1234")

for d in [UPLOAD_DIR, SHARE_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

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

def attendance_path():
    return os.path.join(DATA_DIR, f"attendance_{date.today()}.json")

def notices_path():
    return os.path.join(DATA_DIR, "notices.json")

def quiz_path():
    return os.path.join(DATA_DIR, "quizzes.json")

def quiz_answers_path(quiz_id):
    return os.path.join(DATA_DIR, f"answers_{quiz_id}.json")

def is_teacher():
    return session.get("role") == "teacher"

def get_student_num():
    return session.get("student_num")

def today_str():
    return date.today().strftime("%Y년 %m월 %d일")

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
            if 1 <= num <= STUDENT_COUNT:
                session["role"] = "student"
                session["student_num"] = num
                return redirect(url_for("student_dashboard"))
        except:
            pass
        return render_template("index.html", student_count=STUDENT_COUNT, error="번호를 확인해주세요.")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/student")
def student_dashboard():
    num = get_student_num()
    if not num:
        return redirect(url_for("index"))
    notices      = load_json(notices_path(), [])
    quizzes      = load_json(quiz_path(), [])
    active_quizzes = [q for q in quizzes if q.get("active")]
    shared_files = sorted(os.listdir(SHARE_DIR)) if os.path.exists(SHARE_DIR) else []
    att          = load_json(attendance_path(), {})
    already_checked = str(num) in att
    return render_template("student.html",
        num=num, notices=notices, active_quizzes=active_quizzes,
        shared_files=shared_files, already_checked=already_checked, today=today_str())

@app.route("/attendance/check", methods=["POST"])
def attendance_check():
    num = get_student_num()
    if not num:
        return jsonify({"ok": False, "msg": "로그인 필요"})
    att = load_json(attendance_path(), {})
    if str(num) in att:
        return jsonify({"ok": False, "msg": "이미 출석했어요!"})
    att[str(num)] = datetime.now().strftime("%H:%M:%S")
    save_json(attendance_path(), att)
    return jsonify({"ok": True, "msg": f"{num}번 출석 완료!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    num = get_student_num()
    if not num:
        return jsonify({"ok": False, "msg": "로그인 필요"})
    if "file" not in request.files:
        return jsonify({"ok": False, "msg": "파일이 없어요"})
    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "msg": "파일을 선택해주세요"})
    if not allowed(f.filename):
        return jsonify({"ok": False, "msg": "허용되지 않는 파일 형식이에요"})
    ext  = f.filename.rsplit(".",1)[1].lower()
    ts   = datetime.now().strftime("%H%M%S")
    safe = secure_filename(f.filename)
    name = f"{num}번_{ts}_{safe}"
    f.save(os.path.join(UPLOAD_DIR, name))
    return jsonify({"ok": True, "msg": f"'{f.filename}' 제출 완료!"})

@app.route("/download/<filename>")
def download_shared(filename):
    if not get_student_num() and not is_teacher():
        return redirect(url_for("index"))
    return send_from_directory(SHARE_DIR, filename, as_attachment=True)

@app.route("/quiz/<quiz_id>/submit", methods=["POST"])
def quiz_submit(quiz_id):
    num = get_student_num()
    if not num:
        return jsonify({"ok": False, "msg": "로그인 필요"})
    answers_path = quiz_answers_path(quiz_id)
    answers = load_json(answers_path, {})
    if str(num) in answers:
        return jsonify({"ok": False, "msg": "이미 제출했어요!"})
    data = request.get_json()
    answers[str(num)] = {
        "answers": data.get("answers", {}),
        "submitted_at": datetime.now().strftime("%H:%M:%S")
    }
    save_json(answers_path, answers)
    return jsonify({"ok": True, "msg": "제출 완료!"})

@app.route("/teacher")
def teacher_dashboard():
    if not is_teacher():
        return redirect(url_for("index"))
    att          = load_json(attendance_path(), {})
    notices      = load_json(notices_path(), [])
    quizzes      = load_json(quiz_path(), [])
    shared_files = sorted(os.listdir(SHARE_DIR))
    uploads      = sorted(os.listdir(UPLOAD_DIR))
    checked = sorted([int(k) for k in att.keys()])
    absent  = [n for n in range(1, STUDENT_COUNT+1) if n not in checked]
    for q in quizzes:
        ans = load_json(quiz_answers_path(q["id"]), {})
        q["submit_count"] = len(ans)
    return render_template("teacher.html",
        att=att, checked=checked, absent=absent,
        notices=notices, quizzes=quizzes,
        shared_files=shared_files, uploads=uploads,
        today=today_str(), total=STUDENT_COUNT)

@app.route("/teacher/notice/add", methods=["POST"])
def notice_add():
    if not is_teacher(): return redirect(url_for("index"))
    notices = load_json(notices_path(), [])
    content = request.form.get("content","").strip()
    if content:
        notices.insert(0, {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "content": content,
            "date": datetime.now().strftime("%m/%d %H:%M")
        })
        save_json(notices_path(), notices)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/notice/delete/<nid>")
def notice_delete(nid):
    if not is_teacher(): return redirect(url_for("index"))
    notices = [n for n in load_json(notices_path(), []) if n["id"] != nid]
    save_json(notices_path(), notices)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/share", methods=["POST"])
def teacher_share():
    if not is_teacher(): return redirect(url_for("index"))
    if "file" not in request.files: return redirect(url_for("teacher_dashboard"))
    f = request.files["file"]
    if f.filename and allowed(f.filename):
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

@app.route("/teacher/attendance/export")
def export_attendance():
    if not is_teacher(): return redirect(url_for("index"))
    att = load_json(attendance_path(), {})
    from io import StringIO
    si = StringIO()
    w  = csv.writer(si)
    w.writerow(["번호", "출석", "시각"])
    for n in range(1, STUDENT_COUNT+1):
        key = str(n)
        w.writerow([f"{n}번", "출석" if key in att else "결석", att.get(key, "")])
    return Response(
        "\ufeff" + si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=출석_{date.today()}.csv"}
    )

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
                choices = [c.strip() for c in choices_raw.split(",") if c.strip()]
                qs.append({"text": q_text.strip(), "type": "choice", "choices": choices})
            else:
                qs.append({"text": line, "type": "text"})
        if qs:
            qid = datetime.now().strftime("%Y%m%d%H%M%S")
            quizzes.append({
                "id": qid, "title": title, "qtype": qtype, "questions": qs,
                "active": True, "created": datetime.now().strftime("%m/%d %H:%M")
            })
            save_json(quiz_path(), quizzes)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/toggle/<qid>")
def quiz_toggle(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quizzes = load_json(quiz_path(), [])
    for q in quizzes:
        if q["id"] == qid:
            q["active"] = not q.get("active", True)
    save_json(quiz_path(), quizzes)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/delete/<qid>")
def quiz_delete(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quizzes = [q for q in load_json(quiz_path(), []) if q["id"] != qid]
    save_json(quiz_path(), quizzes)
    ans_path = quiz_answers_path(qid)
    if os.path.exists(ans_path): os.remove(ans_path)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/<qid>/results")
def quiz_results(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quizzes = load_json(quiz_path(), [])
    quiz    = next((q for q in quizzes if q["id"] == qid), None)
    if not quiz: return redirect(url_for("teacher_dashboard"))
    answers = load_json(quiz_answers_path(qid), {})
    return render_template("quiz_results.html",
        quiz=quiz, answers=answers, total=STUDENT_COUNT)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
