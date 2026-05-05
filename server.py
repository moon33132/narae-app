import os, json, csv, random
from datetime import datetime, date
from flask import (Flask, render_template, request, redirect,
    url_for, send_from_directory, jsonify, session, Response)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "narae2025secret")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400 * 30
app.jinja_env.filters['enumerate'] = enumerate

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
SHARE_DIR  = os.path.join(BASE_DIR, "shared")
DATA_DIR   = os.path.join(BASE_DIR, "data")
BOARD_DIR  = os.path.join(BASE_DIR, "board_uploads")
ALLOWED_EXT = {"pdf","hwp","hwpx","docx","xlsx","pptx","jpg","jpeg","png","gif","mp4","mp3","txt","zip"}
STUDENT_COUNT = 22
TEACHER_PW = os.environ.get("TEACHER_PW", "narae1234")

for d in [UPLOAD_DIR, SHARE_DIR, DATA_DIR, BOARD_DIR]:
    os.makedirs(d, exist_ok=True)

def allowed(f): return "." in f and f.rsplit(".",1)[1].lower() in ALLOWED_EXT
def load_json(p, d):
    try:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f: return json.load(f)
    except: pass
    return d
def save_json(p, d):
    with open(p, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def passwords_path():       return os.path.join(DATA_DIR, "passwords.json")
def attendance_path(d=None):
    d = d or date.today().isoformat()
    return os.path.join(DATA_DIR, f"att_{d}.json")
def notices_path():         return os.path.join(DATA_DIR, "notices.json")
def exams_path():           return os.path.join(DATA_DIR, "exams.json")
def exam_answers_path(eid): return os.path.join(DATA_DIR, f"exam_ans_{eid}.json")
def quizzes_path():         return os.path.join(DATA_DIR, "quizzes.json")
def quiz_answers_path(qid): return os.path.join(DATA_DIR, f"quiz_ans_{qid}.json")
def word_tests_path():      return os.path.join(DATA_DIR, "word_tests.json")
def word_answers_path(wid): return os.path.join(DATA_DIR, f"word_ans_{wid}.json")
def boards_path():          return os.path.join(DATA_DIR, "boards.json")
def board_posts_path(bid):  return os.path.join(DATA_DIR, f"board_{bid}.json")
def homework_path():        return os.path.join(DATA_DIR, f"hw_{date.today()}.json")
def homework_items_path():  return os.path.join(DATA_DIR, "hw_items.json")

DEFAULT_HW = [{"id":"hw_1","name":"수학 숙제"},{"id":"hw_2","name":"국어 숙제"},{"id":"hw_3","name":"알림장"}]

def get_hw_items():
    items = load_json(homework_items_path(), [])
    if not items:
        save_json(homework_items_path(), DEFAULT_HW)
        return list(DEFAULT_HW)
    for i, item in enumerate(items):
        if "id" not in item: item["id"] = f"hw_{i+1}"
    return items

_boards_cache = None
def get_boards():
    global _boards_cache
    if _boards_cache is None:
        _boards_cache = load_json(boards_path(), [])
    return _boards_cache
def set_boards(b):
    global _boards_cache
    _boards_cache = b
    save_json(boards_path(), b)

def is_teacher(): return session.get("role") == "teacher"
def get_num():    return session.get("student_num")
def today_str():  return date.today().strftime("%Y년 %m월 %d일")

def record_attendance(num):
    att = load_json(attendance_path(), {})
    if str(num) not in att:
        att[str(num)] = datetime.now().strftime("%H:%M:%S")
        save_json(attendance_path(), att)

def get_all_att_dates():
    return sorted([f.replace("att_","").replace(".json","")
                   for f in os.listdir(DATA_DIR) if f.startswith("att_") and f.endswith(".json")])

WORD_DAYS = {
    1:[{"ko":"사과","en":"apple"},{"ko":"바나나","en":"banana"},{"ko":"학교","en":"school"},{"ko":"친구","en":"friend"},{"ko":"선생님","en":"teacher"},{"ko":"집","en":"house"},{"ko":"물","en":"water"},{"ko":"하늘","en":"sky"},{"ko":"땅","en":"ground"},{"ko":"나무","en":"tree"},{"ko":"꽃","en":"flower"},{"ko":"책","en":"book"},{"ko":"공","en":"ball"},{"ko":"고양이","en":"cat"},{"ko":"개","en":"dog"},{"ko":"새","en":"bird"},{"ko":"물고기","en":"fish"},{"ko":"밥","en":"rice"},{"ko":"우유","en":"milk"},{"ko":"빵","en":"bread"}],
    2:[{"ko":"눈","en":"eye"},{"ko":"코","en":"nose"},{"ko":"입","en":"mouth"},{"ko":"귀","en":"ear"},{"ko":"손","en":"hand"},{"ko":"발","en":"foot"},{"ko":"머리","en":"head"},{"ko":"몸","en":"body"},{"ko":"팔","en":"arm"},{"ko":"다리","en":"leg"},{"ko":"빨간색","en":"red"},{"ko":"파란색","en":"blue"},{"ko":"노란색","en":"yellow"},{"ko":"초록색","en":"green"},{"ko":"흰색","en":"white"},{"ko":"검은색","en":"black"},{"ko":"크다","en":"big"},{"ko":"작다","en":"small"},{"ko":"높다","en":"high"},{"ko":"낮다","en":"low"}],
    3:[{"ko":"아버지","en":"father"},{"ko":"어머니","en":"mother"},{"ko":"형","en":"brother"},{"ko":"언니","en":"sister"},{"ko":"할아버지","en":"grandfather"},{"ko":"할머니","en":"grandmother"},{"ko":"아들","en":"son"},{"ko":"딸","en":"daughter"},{"ko":"가족","en":"family"},{"ko":"아기","en":"baby"},{"ko":"봄","en":"spring"},{"ko":"여름","en":"summer"},{"ko":"가을","en":"autumn"},{"ko":"겨울","en":"winter"},{"ko":"날씨","en":"weather"},{"ko":"비","en":"rain"},{"ko":"눈날씨","en":"snow"},{"ko":"바람","en":"wind"},{"ko":"태양","en":"sun"},{"ko":"달","en":"moon"}],
    4:[{"ko":"아침","en":"morning"},{"ko":"점심","en":"noon"},{"ko":"저녁","en":"evening"},{"ko":"밤","en":"night"},{"ko":"오늘","en":"today"},{"ko":"어제","en":"yesterday"},{"ko":"내일","en":"tomorrow"},{"ko":"일주일","en":"week"},{"ko":"월요일","en":"Monday"},{"ko":"화요일","en":"Tuesday"},{"ko":"수요일","en":"Wednesday"},{"ko":"목요일","en":"Thursday"},{"ko":"금요일","en":"Friday"},{"ko":"토요일","en":"Saturday"},{"ko":"일요일","en":"Sunday"},{"ko":"시간","en":"time"},{"ko":"분","en":"minute"},{"ko":"초","en":"second"},{"ko":"시계","en":"clock"},{"ko":"달력","en":"calendar"}],
    5:[{"ko":"사자","en":"lion"},{"ko":"호랑이","en":"tiger"},{"ko":"코끼리","en":"elephant"},{"ko":"기린","en":"giraffe"},{"ko":"원숭이","en":"monkey"},{"ko":"곰","en":"bear"},{"ko":"토끼","en":"rabbit"},{"ko":"여우","en":"fox"},{"ko":"늑대","en":"wolf"},{"ko":"말","en":"horse"},{"ko":"소","en":"cow"},{"ko":"돼지","en":"pig"},{"ko":"양","en":"sheep"},{"ko":"닭","en":"chicken"},{"ko":"오리","en":"duck"},{"ko":"개구리","en":"frog"},{"ko":"뱀","en":"snake"},{"ko":"거북이","en":"turtle"},{"ko":"나비","en":"butterfly"},{"ko":"벌","en":"bee"}],
    6:[{"ko":"의자","en":"chair"},{"ko":"침대","en":"bed"},{"ko":"창문","en":"window"},{"ko":"문","en":"door"},{"ko":"벽","en":"wall"},{"ko":"바닥","en":"floor"},{"ko":"천장","en":"ceiling"},{"ko":"냉장고","en":"refrigerator"},{"ko":"텔레비전","en":"television"},{"ko":"컴퓨터","en":"computer"},{"ko":"전화기","en":"phone"},{"ko":"칫솔","en":"toothbrush"},{"ko":"비누","en":"soap"},{"ko":"수건","en":"towel"},{"ko":"가방","en":"bag"},{"ko":"신발","en":"shoes"},{"ko":"모자","en":"hat"},{"ko":"셔츠","en":"shirt"},{"ko":"바지","en":"pants"},{"ko":"양말","en":"socks"}],
    7:[{"ko":"수박","en":"watermelon"},{"ko":"딸기","en":"strawberry"},{"ko":"포도","en":"grape"},{"ko":"오렌지","en":"orange"},{"ko":"레몬","en":"lemon"},{"ko":"복숭아","en":"peach"},{"ko":"파인애플","en":"pineapple"},{"ko":"망고","en":"mango"},{"ko":"키위","en":"kiwi"},{"ko":"배","en":"pear"},{"ko":"당근","en":"carrot"},{"ko":"오이","en":"cucumber"},{"ko":"토마토","en":"tomato"},{"ko":"양파","en":"onion"},{"ko":"감자","en":"potato"},{"ko":"고추","en":"pepper"},{"ko":"배추","en":"cabbage"},{"ko":"시금치","en":"spinach"},{"ko":"버섯","en":"mushroom"},{"ko":"마늘","en":"garlic"}],
    8:[{"ko":"달리다","en":"run"},{"ko":"걷다","en":"walk"},{"ko":"점프하다","en":"jump"},{"ko":"수영하다","en":"swim"},{"ko":"날다","en":"fly"},{"ko":"먹다","en":"eat"},{"ko":"마시다","en":"drink"},{"ko":"자다","en":"sleep"},{"ko":"일어나다","en":"wake up"},{"ko":"앉다","en":"sit"},{"ko":"서다","en":"stand"},{"ko":"웃다","en":"laugh"},{"ko":"울다","en":"cry"},{"ko":"말하다","en":"speak"},{"ko":"듣다","en":"listen"},{"ko":"보다","en":"see"},{"ko":"읽다","en":"read"},{"ko":"쓰다","en":"write"},{"ko":"그리다","en":"draw"},{"ko":"놀다","en":"play"}],
    9:[{"ko":"행복하다","en":"happy"},{"ko":"슬프다","en":"sad"},{"ko":"화나다","en":"angry"},{"ko":"무섭다","en":"scared"},{"ko":"놀라다","en":"surprised"},{"ko":"피곤하다","en":"tired"},{"ko":"배고프다","en":"hungry"},{"ko":"목마르다","en":"thirsty"},{"ko":"아프다","en":"sick"},{"ko":"건강하다","en":"healthy"},{"ko":"예쁘다","en":"pretty"},{"ko":"잘생기다","en":"handsome"},{"ko":"착하다","en":"kind"},{"ko":"용감하다","en":"brave"},{"ko":"똑똑하다","en":"smart"},{"ko":"빠르다","en":"fast"},{"ko":"느리다","en":"slow"},{"ko":"강하다","en":"strong"},{"ko":"약하다","en":"weak"},{"ko":"조용하다","en":"quiet"}],
    10:[{"ko":"병원","en":"hospital"},{"ko":"약국","en":"pharmacy"},{"ko":"은행","en":"bank"},{"ko":"우체국","en":"post office"},{"ko":"경찰서","en":"police station"},{"ko":"소방서","en":"fire station"},{"ko":"시장","en":"market"},{"ko":"가게","en":"store"},{"ko":"식당","en":"restaurant"},{"ko":"카페","en":"cafe"},{"ko":"공원","en":"park"},{"ko":"도서관","en":"library"},{"ko":"박물관","en":"museum"},{"ko":"영화관","en":"cinema"},{"ko":"공항","en":"airport"},{"ko":"기차역","en":"train station"},{"ko":"버스정류장","en":"bus stop"},{"ko":"지하철","en":"subway"},{"ko":"택시","en":"taxi"},{"ko":"자전거","en":"bicycle"}],
    11:[{"ko":"수학","en":"math"},{"ko":"과학","en":"science"},{"ko":"영어","en":"English"},{"ko":"국어","en":"Korean"},{"ko":"사회","en":"social studies"},{"ko":"음악","en":"music"},{"ko":"미술","en":"art"},{"ko":"체육","en":"physical education"},{"ko":"역사","en":"history"},{"ko":"지리","en":"geography"},{"ko":"연필","en":"pencil"},{"ko":"지우개","en":"eraser"},{"ko":"자","en":"ruler"},{"ko":"가위","en":"scissors"},{"ko":"풀","en":"glue"},{"ko":"색연필","en":"colored pencil"},{"ko":"스케치북","en":"sketchbook"},{"ko":"알림장","en":"planner"},{"ko":"교과서","en":"textbook"},{"ko":"공책","en":"notebook"}],
    12:[{"ko":"비행기","en":"airplane"},{"ko":"배선박","en":"ship"},{"ko":"자동차","en":"car"},{"ko":"버스","en":"bus"},{"ko":"기차","en":"train"},{"ko":"헬리콥터","en":"helicopter"},{"ko":"로켓","en":"rocket"},{"ko":"오토바이","en":"motorcycle"},{"ko":"트럭","en":"truck"},{"ko":"소방차","en":"fire truck"},{"ko":"구급차","en":"ambulance"},{"ko":"경찰차","en":"police car"},{"ko":"스쿠터","en":"scooter"},{"ko":"킥보드","en":"kickboard"},{"ko":"보트","en":"boat"},{"ko":"잠수함","en":"submarine"},{"ko":"우주선","en":"spaceship"},{"ko":"열기구","en":"hot air balloon"},{"ko":"지하철","en":"subway"},{"ko":"케이블카","en":"cable car"}],
    13:[{"ko":"지구","en":"Earth"},{"ko":"달천체","en":"moon"},{"ko":"태양","en":"sun"},{"ko":"별","en":"star"},{"ko":"행성","en":"planet"},{"ko":"우주","en":"space"},{"ko":"산","en":"mountain"},{"ko":"강","en":"river"},{"ko":"바다","en":"ocean"},{"ko":"호수","en":"lake"},{"ko":"섬","en":"island"},{"ko":"사막","en":"desert"},{"ko":"숲","en":"forest"},{"ko":"초원","en":"meadow"},{"ko":"동굴","en":"cave"},{"ko":"폭포","en":"waterfall"},{"ko":"화산","en":"volcano"},{"ko":"빙하","en":"glacier"},{"ko":"평야","en":"plain"},{"ko":"계곡","en":"valley"}],
    14:[{"ko":"의사","en":"doctor"},{"ko":"간호사","en":"nurse"},{"ko":"선생님직업","en":"teacher"},{"ko":"경찰관","en":"police officer"},{"ko":"소방관","en":"firefighter"},{"ko":"요리사","en":"chef"},{"ko":"운전기사","en":"driver"},{"ko":"농부","en":"farmer"},{"ko":"어부","en":"fisherman"},{"ko":"화가","en":"painter"},{"ko":"음악가","en":"musician"},{"ko":"배우","en":"actor"},{"ko":"운동선수","en":"athlete"},{"ko":"과학자","en":"scientist"},{"ko":"엔지니어","en":"engineer"},{"ko":"건축가","en":"architect"},{"ko":"변호사","en":"lawyer"},{"ko":"기자","en":"journalist"},{"ko":"우주비행사","en":"astronaut"},{"ko":"탐험가","en":"explorer"}],
    15:[{"ko":"축구","en":"soccer"},{"ko":"농구","en":"basketball"},{"ko":"야구","en":"baseball"},{"ko":"테니스","en":"tennis"},{"ko":"배드민턴","en":"badminton"},{"ko":"수영스포츠","en":"swimming"},{"ko":"태권도","en":"taekwondo"},{"ko":"체조","en":"gymnastics"},{"ko":"달리기","en":"running"},{"ko":"자전거타기","en":"cycling"},{"ko":"스키","en":"skiing"},{"ko":"볼링","en":"bowling"},{"ko":"골프","en":"golf"},{"ko":"탁구","en":"table tennis"},{"ko":"배구","en":"volleyball"},{"ko":"권투","en":"boxing"},{"ko":"레슬링","en":"wrestling"},{"ko":"유도","en":"judo"},{"ko":"승마","en":"horse riding"},{"ko":"양궁","en":"archery"}],
    16:[{"ko":"피아노","en":"piano"},{"ko":"기타","en":"guitar"},{"ko":"바이올린","en":"violin"},{"ko":"첼로","en":"cello"},{"ko":"플루트","en":"flute"},{"ko":"드럼","en":"drums"},{"ko":"트럼펫","en":"trumpet"},{"ko":"색소폰","en":"saxophone"},{"ko":"하모니카","en":"harmonica"},{"ko":"리코더","en":"recorder"},{"ko":"노래","en":"song"},{"ko":"연주하다","en":"play"},{"ko":"박자","en":"beat"},{"ko":"악보","en":"score"},{"ko":"작곡","en":"composition"},{"ko":"지휘","en":"conduct"},{"ko":"합창","en":"chorus"},{"ko":"오케스트라","en":"orchestra"},{"ko":"콘서트","en":"concert"},{"ko":"악기","en":"instrument"}],
    17:[{"ko":"일숫자","en":"one"},{"ko":"이숫자","en":"two"},{"ko":"삼숫자","en":"three"},{"ko":"사숫자","en":"four"},{"ko":"오숫자","en":"five"},{"ko":"육숫자","en":"six"},{"ko":"칠숫자","en":"seven"},{"ko":"팔숫자","en":"eight"},{"ko":"구숫자","en":"nine"},{"ko":"십숫자","en":"ten"},{"ko":"더하기","en":"plus"},{"ko":"빼기","en":"minus"},{"ko":"곱하기","en":"multiply"},{"ko":"나누기","en":"divide"},{"ko":"같다","en":"equal"},{"ko":"크다수학","en":"greater"},{"ko":"작다수학","en":"less"},{"ko":"반","en":"half"},{"ko":"두배","en":"double"},{"ko":"합계","en":"total"}],
    18:[{"ko":"한국","en":"Korea"},{"ko":"미국","en":"America"},{"ko":"영국","en":"England"},{"ko":"중국","en":"China"},{"ko":"일본","en":"Japan"},{"ko":"프랑스","en":"France"},{"ko":"독일","en":"Germany"},{"ko":"이탈리아","en":"Italy"},{"ko":"스페인","en":"Spain"},{"ko":"러시아","en":"Russia"},{"ko":"브라질","en":"Brazil"},{"ko":"호주","en":"Australia"},{"ko":"캐나다","en":"Canada"},{"ko":"인도","en":"India"},{"ko":"멕시코","en":"Mexico"},{"ko":"아프리카","en":"Africa"},{"ko":"유럽","en":"Europe"},{"ko":"아시아","en":"Asia"},{"ko":"남미","en":"South America"},{"ko":"북미","en":"North America"}],
    19:[{"ko":"컴퓨터기기","en":"computer"},{"ko":"스마트폰","en":"smartphone"},{"ko":"태블릿","en":"tablet"},{"ko":"인터넷","en":"internet"},{"ko":"소셜미디어","en":"social media"},{"ko":"이메일","en":"email"},{"ko":"비밀번호","en":"password"},{"ko":"검색하다","en":"search"},{"ko":"다운로드","en":"download"},{"ko":"업로드","en":"upload"},{"ko":"앱","en":"app"},{"ko":"게임","en":"game"},{"ko":"로봇","en":"robot"},{"ko":"인공지능","en":"artificial intelligence"},{"ko":"드론","en":"drone"},{"ko":"가상현실","en":"virtual reality"},{"ko":"프로그래밍","en":"programming"},{"ko":"코딩","en":"coding"},{"ko":"소프트웨어","en":"software"},{"ko":"하드웨어","en":"hardware"}],
    20:[{"ko":"아침식사","en":"breakfast"},{"ko":"점심식사","en":"lunch"},{"ko":"저녁식사","en":"dinner"},{"ko":"간식","en":"snack"},{"ko":"요리하다","en":"cook"},{"ko":"굽다","en":"bake"},{"ko":"끓이다","en":"boil"},{"ko":"볶다","en":"stir-fry"},{"ko":"달다맛","en":"sweet"},{"ko":"짜다맛","en":"salty"},{"ko":"맵다","en":"spicy"},{"ko":"쓰다맛","en":"bitter"},{"ko":"시다맛","en":"sour"},{"ko":"맛있다","en":"delicious"},{"ko":"배부르다","en":"full"},{"ko":"접시","en":"plate"},{"ko":"컵","en":"cup"},{"ko":"젓가락","en":"chopsticks"},{"ko":"숟가락","en":"spoon"},{"ko":"포크","en":"fork"}],
    21:[{"ko":"인사하다","en":"greet"},{"ko":"소개하다","en":"introduce"},{"ko":"감사하다","en":"thank"},{"ko":"사과하다","en":"apologize"},{"ko":"축하하다","en":"congratulate"},{"ko":"초대하다","en":"invite"},{"ko":"부탁하다","en":"ask a favor"},{"ko":"거절하다","en":"refuse"},{"ko":"허락하다","en":"allow"},{"ko":"금지하다","en":"forbid"},{"ko":"동의하다","en":"agree"},{"ko":"반대하다","en":"disagree"},{"ko":"제안하다","en":"suggest"},{"ko":"설명하다","en":"explain"},{"ko":"물어보다","en":"ask"},{"ko":"대답하다","en":"answer"},{"ko":"약속하다","en":"promise"},{"ko":"도움을주다","en":"help"},{"ko":"칭찬하다","en":"praise"},{"ko":"비판하다","en":"criticize"}],
    22:[{"ko":"수업","en":"class"},{"ko":"숙제","en":"homework"},{"ko":"시험","en":"exam"},{"ko":"성적","en":"grade"},{"ko":"졸업","en":"graduation"},{"ko":"입학","en":"admission"},{"ko":"방학","en":"vacation"},{"ko":"운동회","en":"sports day"},{"ko":"소풍","en":"field trip"},{"ko":"발표","en":"presentation"},{"ko":"토론","en":"discussion"},{"ko":"실험","en":"experiment"},{"ko":"조사","en":"research"},{"ko":"독서","en":"reading"},{"ko":"일기","en":"diary"},{"ko":"편지","en":"letter"},{"ko":"시문학","en":"poem"},{"ko":"이야기","en":"story"},{"ko":"만화","en":"comic"},{"ko":"학교생활","en":"school life"}],
    23:[{"ko":"환경","en":"environment"},{"ko":"오염","en":"pollution"},{"ko":"재활용","en":"recycling"},{"ko":"쓰레기","en":"trash"},{"ko":"에너지","en":"energy"},{"ko":"전기","en":"electricity"},{"ko":"태양에너지","en":"solar energy"},{"ko":"바람에너지","en":"wind energy"},{"ko":"온난화","en":"global warming"},{"ko":"기후변화","en":"climate change"},{"ko":"멸종위기","en":"endangered"},{"ko":"보호하다","en":"protect"},{"ko":"자연","en":"nature"},{"ko":"생태계","en":"ecosystem"},{"ko":"먹이사슬","en":"food chain"},{"ko":"광합성","en":"photosynthesis"},{"ko":"진화","en":"evolution"},{"ko":"화석","en":"fossil"},{"ko":"공룡","en":"dinosaur"},{"ko":"멸종","en":"extinction"}],
    24:[{"ko":"건물","en":"building"},{"ko":"아파트","en":"apartment"},{"ko":"교회","en":"church"},{"ko":"성당","en":"cathedral"},{"ko":"사원","en":"temple"},{"ko":"궁궐","en":"palace"},{"ko":"성건축","en":"castle"},{"ko":"탑","en":"tower"},{"ko":"다리건축","en":"bridge"},{"ko":"터널","en":"tunnel"},{"ko":"도로","en":"road"},{"ko":"고속도로","en":"highway"},{"ko":"골목","en":"alley"},{"ko":"광장","en":"plaza"},{"ko":"공사장","en":"construction site"},{"ko":"주차장","en":"parking lot"},{"ko":"놀이터","en":"playground"},{"ko":"운동장","en":"sports field"},{"ko":"수영장","en":"swimming pool"},{"ko":"체육관","en":"gymnasium"}],
    25:[{"ko":"생각하다","en":"think"},{"ko":"느끼다","en":"feel"},{"ko":"믿다","en":"believe"},{"ko":"알다","en":"know"},{"ko":"기억하다","en":"remember"},{"ko":"잊다","en":"forget"},{"ko":"이해하다","en":"understand"},{"ko":"배우다","en":"learn"},{"ko":"가르치다","en":"teach"},{"ko":"연습하다","en":"practice"},{"ko":"노력하다","en":"try hard"},{"ko":"성공하다","en":"succeed"},{"ko":"실패하다","en":"fail"},{"ko":"포기하다","en":"give up"},{"ko":"계속하다","en":"continue"},{"ko":"시작하다","en":"start"},{"ko":"끝내다","en":"finish"},{"ko":"결정하다","en":"decide"},{"ko":"선택하다","en":"choose"},{"ko":"변화하다","en":"change"}],
    26:[{"ko":"전쟁","en":"war"},{"ko":"평화","en":"peace"},{"ko":"역사","en":"history"},{"ko":"문화","en":"culture"},{"ko":"전통","en":"tradition"},{"ko":"축제","en":"festival"},{"ko":"명절","en":"holiday"},{"ko":"설날","en":"Lunar New Year"},{"ko":"추석","en":"Chuseok"},{"ko":"크리스마스","en":"Christmas"},{"ko":"생일","en":"birthday"},{"ko":"결혼","en":"wedding"},{"ko":"졸업식","en":"graduation ceremony"},{"ko":"입학식","en":"entrance ceremony"},{"ko":"개막식","en":"opening ceremony"},{"ko":"기념일","en":"anniversary"},{"ko":"올림픽","en":"Olympics"},{"ko":"월드컵","en":"World Cup"},{"ko":"박람회","en":"fair"},{"ko":"행사","en":"event"}],
    27:[{"ko":"돈","en":"money"},{"ko":"가격","en":"price"},{"ko":"할인","en":"discount"},{"ko":"세금","en":"tax"},{"ko":"저축","en":"savings"},{"ko":"투자","en":"investment"},{"ko":"수입소득","en":"income"},{"ko":"지출","en":"expense"},{"ko":"예산","en":"budget"},{"ko":"보험","en":"insurance"},{"ko":"대출","en":"loan"},{"ko":"이자","en":"interest"},{"ko":"주식","en":"stock"},{"ko":"부동산","en":"real estate"},{"ko":"경제","en":"economy"},{"ko":"무역","en":"trade"},{"ko":"수출","en":"export"},{"ko":"소비","en":"consumption"},{"ko":"생산","en":"production"},{"ko":"시장경제","en":"market"}],
    28:[{"ko":"병질병","en":"disease"},{"ko":"건강","en":"health"},{"ko":"운동건강","en":"exercise"},{"ko":"식단","en":"diet"},{"ko":"수면잠","en":"sleep"},{"ko":"스트레스","en":"stress"},{"ko":"휴식","en":"rest"},{"ko":"명상","en":"meditation"},{"ko":"요가","en":"yoga"},{"ko":"마라톤","en":"marathon"},{"ko":"비타민","en":"vitamin"},{"ko":"단백질","en":"protein"},{"ko":"칼로리","en":"calorie"},{"ko":"영양소","en":"nutrient"},{"ko":"채소","en":"vegetable"},{"ko":"과일","en":"fruit"},{"ko":"견과류","en":"nuts"},{"ko":"유제품","en":"dairy"},{"ko":"음료","en":"beverage"},{"ko":"물건강","en":"water"}],
    29:[{"ko":"예술","en":"art"},{"ko":"그림","en":"painting"},{"ko":"조각","en":"sculpture"},{"ko":"사진촬영","en":"photography"},{"ko":"영화","en":"film"},{"ko":"연극","en":"theater"},{"ko":"뮤지컬","en":"musical"},{"ko":"오페라","en":"opera"},{"ko":"발레","en":"ballet"},{"ko":"무용","en":"dance"},{"ko":"전시회","en":"exhibition"},{"ko":"공연","en":"performance"},{"ko":"작가","en":"author"},{"ko":"소설","en":"novel"},{"ko":"시집","en":"poetry book"},{"ko":"만화책","en":"comic book"},{"ko":"잡지","en":"magazine"},{"ko":"신문","en":"newspaper"},{"ko":"출판","en":"publish"},{"ko":"번역","en":"translate"}],
    30:[{"ko":"꿈","en":"dream"},{"ko":"목표","en":"goal"},{"ko":"미래","en":"future"},{"ko":"과거","en":"past"},{"ko":"현재","en":"present"},{"ko":"변화","en":"change"},{"ko":"도전","en":"challenge"},{"ko":"기회","en":"opportunity"},{"ko":"위기","en":"crisis"},{"ko":"해결","en":"solution"},{"ko":"창의적","en":"creative"},{"ko":"혁신","en":"innovation"},{"ko":"리더십","en":"leadership"},{"ko":"팀워크","en":"teamwork"},{"ko":"소통","en":"communication"},{"ko":"존중","en":"respect"},{"ko":"책임","en":"responsibility"},{"ko":"정직","en":"honesty"},{"ko":"용기","en":"courage"},{"ko":"희망","en":"hope"}],
}

@app.route("/")
def index():
    return render_template("index.html", student_count=STUDENT_COUNT)

@app.route("/login", methods=["POST"])
def login():
    role = request.form.get("role")
    if role == "teacher":
        if request.form.get("password","") == TEACHER_PW:
            session.permanent = True
            session["role"] = "teacher"
            return redirect(url_for("teacher_dashboard"))
        return render_template("index.html", student_count=STUDENT_COUNT, error="비밀번호가 틀렸어요.")
    elif role == "student":
        try:
            num = int(request.form.get("student_num",""))
            pw  = request.form.get("password","").strip()
            assert 1 <= num <= STUDENT_COUNT
        except:
            return render_template("index.html", student_count=STUDENT_COUNT, error="번호를 확인해주세요.")
        passwords = load_json(passwords_path(), {})
        key = str(num)
        if key not in passwords:
            if pw == "": return render_template("register.html", num=num)
            if len(pw)==4 and pw.isdigit():
                passwords[key]=pw; save_json(passwords_path(), passwords)
                session.permanent=True; session.update({"role":"student","student_num":num})
                record_attendance(num)
                return redirect(url_for("student_dashboard"))
            return render_template("register.html", num=num, error="숫자 4자리로 입력해주세요.")
        if pw == "": return render_template("index.html", student_count=STUDENT_COUNT, need_pw=num)
        if passwords[key] == pw:
            session.permanent=True; session.update({"role":"student","student_num":num})
            record_attendance(num); return redirect(url_for("student_dashboard"))
        return render_template("index.html", student_count=STUDENT_COUNT, error="비밀번호가 틀렸어요.", need_pw=num)
    return redirect(url_for("index"))

@app.route("/register", methods=["POST"])
def register():
    try: num=int(request.form.get("num","")); assert 1<=num<=STUDENT_COUNT
    except: return redirect(url_for("index"))
    pw=request.form.get("new_pw","").strip()
    if len(pw)!=4 or not pw.isdigit():
        return render_template("register.html", num=num, error="숫자 4자리로 입력해주세요.")
    passwords=load_json(passwords_path(),{})
    passwords[str(num)]=pw; save_json(passwords_path(),passwords)
    session.permanent=True; session.update({"role":"student","student_num":num})
    record_attendance(num); return redirect(url_for("student_dashboard"))

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

@app.route("/student")
def student_dashboard():
    num = get_num()
    if not num: return redirect(url_for("index"))
    quizzes      = [q for q in load_json(quizzes_path(),[]) if q.get("active")]
    exams        = load_json(exams_path(),[])
    active_exams = [e for e in exams if e.get("active")]
    word_tests   = load_json(word_tests_path(),[])
    active_wt    = [w for w in word_tests if w.get("active")]
    shared_files = sorted(os.listdir(SHARE_DIR))
    submitted_exams = {e["id"] for e in exams if str(num) in load_json(exam_answers_path(e["id"]),{})}
    submitted_wt    = {w["id"] for w in word_tests if str(num) in load_json(word_answers_path(w["id"]),{})}
    hw_items    = get_hw_items()
    hw_done     = load_json(homework_path(), {}).get(str(num), [])
    open_boards = [b for b in get_boards() if b.get("open")]
    notices     = load_json(notices_path(), [])
    return render_template("student.html", num=num, today=today_str(),
        active_quizzes=quizzes, active_exams=active_exams,
        active_word_tests=active_wt, submitted_exams=submitted_exams,
        submitted_wt=submitted_wt, shared_files=shared_files,
        hw_items=hw_items, hw_done=hw_done,
        open_boards=open_boards, notices=notices)

@app.route("/upload", methods=["POST"])
def upload_file():
    num=get_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    f=request.files.get("file")
    if not f or not f.filename or not allowed(f.filename):
        return jsonify({"ok":False,"msg":"파일을 확인해주세요"})
    ts=datetime.now().strftime("%H%M%S")
    f.save(os.path.join(UPLOAD_DIR,f"{num}번_{ts}_{secure_filename(f.filename)}"))
    return jsonify({"ok":True,"msg":f"'{f.filename}' 제출 완료!"})

@app.route("/download/<filename>")
def download_shared(filename):
    if not get_num() and not is_teacher(): return redirect(url_for("index"))
    return send_from_directory(SHARE_DIR, filename, as_attachment=True)

@app.route("/quiz/<qid>/submit", methods=["POST"])
def quiz_submit(qid):
    num=get_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    answers=load_json(quiz_answers_path(qid),{})
    if str(num) in answers: return jsonify({"ok":False,"msg":"이미 제출했어요!"})
    data=request.get_json()
    answers[str(num)]={"answers":data.get("answers",{}),"submitted_at":datetime.now().strftime("%H:%M:%S")}
    save_json(quiz_answers_path(qid),answers)
    return jsonify({"ok":True,"msg":"제출 완료!"})

@app.route("/exam/<eid>/submit", methods=["POST"])
def exam_submit(eid):
    num=get_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    exams=load_json(exams_path(),[])
    exam=next((e for e in exams if e["id"]==eid),None)
    if not exam: return jsonify({"ok":False,"msg":"시험 없음"})
    all_ans=load_json(exam_answers_path(eid),{})
    if str(num) in all_ans: return jsonify({"ok":False,"msg":"이미 제출했어요!"})
    data=request.get_json()
    student_ans=data.get("answers",{})
    answer_key=exam.get("answer_key",{})
    q_count=exam.get("question_count",20)
    per_q=100/q_count if q_count else 5
    score,results=0,{}
    for i in range(1,q_count+1):
        k=str(i); s=student_ans.get(k,"").strip(); c=str(answer_key.get(k,"")).strip()
        ok=(s.lower()==c.lower()) if c else None
        results[k]={"student":s,"correct":c,"is_right":ok}
        if ok: score+=per_q
    score=round(score)
    all_ans[str(num)]={"answers":student_ans,"results":results,"score":score,
        "submitted_at":datetime.now().strftime("%H:%M:%S"),"date":date.today().isoformat()}
    save_json(exam_answers_path(eid),all_ans)
    return jsonify({"ok":True,"msg":f"제출 완료! 점수: {score}점","score":score,"results":results})

@app.route("/homework/check", methods=["POST"])
def homework_check():
    num=get_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    data=request.get_json()
    item_id=data.get("item_id",""); checked=data.get("checked",False)
    hw=load_json(homework_path(),{})
    key=str(num)
    if key not in hw: hw[key]=[]
    if checked and item_id not in hw[key]: hw[key].append(item_id)
    elif not checked and item_id in hw[key]: hw[key].remove(item_id)
    save_json(homework_path(),hw)
    return jsonify({"ok":True})

@app.route("/word_test/<wid>")
def word_test_page(wid):
    num=get_num()
    if not num: return redirect(url_for("index"))
    tests=load_json(word_tests_path(),[])
    test=next((w for w in tests if w["id"]==wid),None)
    if not test or not test.get("active"): return redirect(url_for("student_dashboard"))
    all_ans=load_json(word_answers_path(wid),{})
    if str(num) in all_ans:
        return render_template("word_test_result.html",num=num,test=test,result=all_ans[str(num)])
    words=list(enumerate(test["words"]))
    random.seed(num); random.shuffle(words)
    return render_template("word_test.html",num=num,test=test,words=words)

@app.route("/word_test/<wid>/submit", methods=["POST"])
def word_test_submit(wid):
    num=get_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    tests=load_json(word_tests_path(),[])
    test=next((w for w in tests if w["id"]==wid),None)
    if not test: return jsonify({"ok":False,"msg":"시험 없음"})
    all_ans=load_json(word_answers_path(wid),{})
    if str(num) in all_ans: return jsonify({"ok":False,"msg":"이미 제출했어요!"})
    data=request.get_json()
    student=data.get("answers",{})
    direction=test.get("direction","ko_to_en")
    words=test["words"]; total=len(words)
    shuffled=list(enumerate(words)); random.seed(num); random.shuffle(shuffled)
    score,results=0,[]
    for screen_pos,(orig_i,word) in enumerate(shuffled):
        s_ans=student.get(str(orig_i),"").strip()
        if direction=="ko_to_en": correct=word["en"].strip(); question=word["ko"]
        elif direction=="en_to_ko": correct=word["ko"].strip(); question=word["en"]
        else:
            if screen_pos%2==0: correct=word["en"].strip(); question=word["ko"]
            else: correct=word["ko"].strip(); question=word["en"]
        is_right=s_ans.lower()==correct.lower()
        if is_right: score+=1
        results.append({"q":question,"correct":correct,"student":s_ans,"is_right":is_right})
    score_pct=round(score/total*100) if total else 0
    record={"answers":student,"results":results,"score":score,"total":total,
            "score_pct":score_pct,"submitted_at":datetime.now().strftime("%H:%M:%S"),
            "date":date.today().isoformat()}
    all_ans[str(num)]=record; save_json(word_answers_path(wid),all_ans)
    return jsonify({"ok":True,"score":score,"total":total,"score_pct":score_pct,"results":results})

@app.route("/wordbook")
def wordbook():
    num=get_num()
    if not num: return redirect(url_for("index"))
    return render_template("wordbook.html",num=num,word_days=WORD_DAYS)

@app.route("/boards")
def boards_list():
    num=get_num()
    if not num and not is_teacher(): return redirect(url_for("index"))
    boards=get_boards()
    if not is_teacher(): boards=[b for b in boards if b.get("open")]
    return render_template("boards.html",boards=boards,is_teacher=is_teacher(),num=num)

@app.route("/board/<bid>")
def board_view(bid):
    num=get_num()
    if not num and not is_teacher(): return redirect(url_for("index"))
    b=next((x for x in get_boards() if x["id"]==bid),None)
    if not b: return redirect(url_for("boards_list"))
    if not is_teacher() and not b.get("open"): return redirect(url_for("student_dashboard"))
    posts=load_json(board_posts_path(bid),[])
    return render_template("board.html",posts=posts,num=num,is_teacher=is_teacher(),board=b)

@app.route("/board/<bid>/post", methods=["POST"])
def board_post(bid):
    num=get_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    b=next((x for x in get_boards() if x["id"]==bid),None)
    if not b or not b.get("open"): return jsonify({"ok":False,"msg":"닫힌 게시판이에요"})
    content=request.form.get("content","").strip()
    image_url=""
    if "image" in request.files:
        f=request.files["image"]
        if f and f.filename:
            ext=f.filename.rsplit(".",1)[-1].lower()
            if ext in {"jpg","jpeg","png","gif","webp"}:
                ts=datetime.now().strftime("%Y%m%d%H%M%S%f")
                fname=f"{num}번_{ts}.{ext}"
                f.save(os.path.join(BOARD_DIR,fname))
                image_url=f"/board_image/{fname}"
    if not content and not image_url:
        return jsonify({"ok":False,"msg":"내용이나 사진을 추가해주세요"})
    posts=load_json(board_posts_path(bid),[])
    posts.insert(0,{"id":datetime.now().strftime("%Y%m%d%H%M%S%f"),"num":num,
        "content":content,"image_url":image_url,"created":datetime.now().strftime("%m/%d %H:%M")})
    save_json(board_posts_path(bid),posts)
    return jsonify({"ok":True})

@app.route("/board/<bid>/delete/<pid>")
def board_delete_post(bid,pid):
    if not get_num() and not is_teacher(): return redirect(url_for("index"))
    num=get_num()
    posts=load_json(board_posts_path(bid),[])
    new_posts=[]
    for p in posts:
        if p["id"]==pid:
            if is_teacher() or p["num"]==num:
                if p.get("image_url"):
                    fpath=os.path.join(BOARD_DIR,p["image_url"].split("/")[-1])
                    if os.path.exists(fpath): os.remove(fpath)
                continue
        new_posts.append(p)
    save_json(board_posts_path(bid),new_posts)
    return jsonify({"ok":True})

@app.route("/board_image/<filename>")
def board_image(filename):
    return send_from_directory(BOARD_DIR, filename)

@app.route("/teacher")
def teacher_dashboard():
    if not is_teacher(): return redirect(url_for("index"))
    att=load_json(attendance_path(),{})
    checked=sorted([int(k) for k in att])
    absent=[n for n in range(1,STUDENT_COUNT+1) if n not in checked]
    notices=load_json(notices_path(),[])
    quizzes=load_json(quizzes_path(),[])
    exams=load_json(exams_path(),[])
    word_tests=load_json(word_tests_path(),[])
    shared_files=sorted(os.listdir(SHARE_DIR))
    uploads=sorted(os.listdir(UPLOAD_DIR))
    passwords=load_json(passwords_path(),{})
    registered=[int(k) for k in passwords]
    hw_items=get_hw_items()
    hw_today=load_json(homework_path(),{})
    boards=get_boards()
    for q in quizzes: q["submit_count"]=len(load_json(quiz_answers_path(q["id"]),{}))
    for e in exams:
        ans=load_json(exam_answers_path(e["id"]),{})
        e["submit_count"]=len(ans)
        scores=[v["score"] for v in ans.values() if "score" in v]
        e["avg_score"]=round(sum(scores)/len(scores)) if scores else "-"
    for w in word_tests:
        ans=load_json(word_answers_path(w["id"]),{})
        w["submit_count"]=len(ans)
        scores=[v["score_pct"] for v in ans.values() if "score_pct" in v]
        w["avg_score"]=round(sum(scores)/len(scores)) if scores else "-"
    return render_template("teacher.html",
        att=att,checked=checked,absent=absent,notices=notices,
        quizzes=quizzes,exams=exams,word_tests=word_tests,
        shared_files=shared_files,uploads=uploads,today=today_str(),
        total=STUDENT_COUNT,registered=registered,
        hw_items=hw_items,hw_today=hw_today,boards=boards)

@app.route("/teacher/notice/add", methods=["POST"])
def notice_add():
    if not is_teacher(): return redirect(url_for("index"))
    notices=load_json(notices_path(),[])
    content=request.form.get("content","").strip()
    if content:
        notices.insert(0,{"id":datetime.now().strftime("%Y%m%d%H%M%S"),
            "content":content,"date":datetime.now().strftime("%m/%d %H:%M")})
        save_json(notices_path(),notices)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/notice/delete/<nid>")
def notice_delete(nid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(notices_path(),[n for n in load_json(notices_path(),[]) if n["id"]!=nid])
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/share", methods=["POST"])
def teacher_share():
    if not is_teacher(): return redirect(url_for("teacher_dashboard"))
    f=request.files.get("file")
    if f and f.filename and allowed(f.filename):
        f.save(os.path.join(SHARE_DIR,secure_filename(f.filename)))
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/share/delete/<filename>")
def teacher_share_delete(filename):
    if not is_teacher(): return redirect(url_for("index"))
    p=os.path.join(SHARE_DIR,secure_filename(filename))
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/uploads/<filename>")
def teacher_download_upload(filename):
    if not is_teacher(): return redirect(url_for("index"))
    return send_from_directory(UPLOAD_DIR,filename,as_attachment=True)

@app.route("/teacher/uploads/delete/<filename>")
def teacher_delete_upload(filename):
    if not is_teacher(): return redirect(url_for("index"))
    p=os.path.join(UPLOAD_DIR,secure_filename(filename))
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/attendance/export")
def export_attendance():
    if not is_teacher(): return redirect(url_for("index"))
    att=load_json(attendance_path(),{})
    from io import StringIO
    si=StringIO(); w=csv.writer(si)
    w.writerow(["번호","출석","시각"])
    for n in range(1,STUDENT_COUNT+1):
        k=str(n); w.writerow([f"{n}번","출석" if k in att else "결석",att.get(k,"")])
    return Response("\ufeff"+si.getvalue(),mimetype="text/csv",
        headers={"Content-Disposition":f"attachment;filename=출석_{date.today()}.csv"})

@app.route("/teacher/exam/add", methods=["POST"])
def exam_add():
    if not is_teacher(): return redirect(url_for("index"))
    exams=load_json(exams_path(),[])
    title=request.form.get("title","").strip()
    if not title: return redirect(url_for("teacher_dashboard"))
    q_count=int(request.form.get("question_count",20))
    answer_key={}
    for i in range(1,q_count+1):
        ans=request.form.get(f"ans_{i}","").strip()
        if ans: answer_key[str(i)]=ans
    eid=datetime.now().strftime("%Y%m%d%H%M%S")
    exams.append({"id":eid,"title":title,"question_count":q_count,
        "answer_key":answer_key,"active":True,"created":datetime.now().strftime("%m/%d %H:%M")})
    save_json(exams_path(),exams)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/toggle/<eid>")
def exam_toggle(eid):
    if not is_teacher(): return redirect(url_for("index"))
    exams=load_json(exams_path(),[])
    for e in exams:
        if e["id"]==eid: e["active"]=not e.get("active",True)
    save_json(exams_path(),exams); return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/delete/<eid>")
def exam_delete(eid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(exams_path(),[e for e in load_json(exams_path(),[]) if e["id"]!=eid])
    p=exam_answers_path(eid)
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/<eid>/results")
def exam_results(eid):
    if not is_teacher(): return redirect(url_for("index"))
    exam=next((e for e in load_json(exams_path(),[]) if e["id"]==eid),None)
    if not exam: return redirect(url_for("teacher_dashboard"))
    return render_template("exam_results.html",exam=exam,
        answers=load_json(exam_answers_path(eid),{}),total=STUDENT_COUNT)

@app.route("/teacher/quiz/add", methods=["POST"])
def quiz_add():
    if not is_teacher(): return redirect(url_for("index"))
    quizzes=load_json(quizzes_path(),[])
    title=request.form.get("title","").strip()
    if not title: return redirect(url_for("teacher_dashboard"))
    import re as _re
    qs=[]
    text_keys=sorted([k for k in request.form.keys() if _re.match(r"qq_text_\d+$",k)],
        key=lambda k:int(_re.search(r"\d+$",k).group()))
    for key in text_keys:
        q_text=request.form.get(key,"").strip()
        if not q_text: continue
        n=_re.search(r"\d+$",key).group()
        qs.append({"text":q_text,"type":"ox","answer":"","choices":["O","X"]})
    if qs:
        qid=datetime.now().strftime("%Y%m%d%H%M%S")
        quizzes.append({"id":qid,"title":title,"questions":qs,
            "active":True,"created":datetime.now().strftime("%m/%d %H:%M")})
        save_json(quizzes_path(),quizzes)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/toggle/<qid>")
def quiz_toggle(qid):
    if not is_teacher(): return redirect(url_for("index"))
    qs=load_json(quizzes_path(),[])
    for q in qs:
        if q["id"]==qid: q["active"]=not q.get("active",True)
    save_json(quizzes_path(),qs); return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/delete/<qid>")
def quiz_delete(qid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(quizzes_path(),[q for q in load_json(quizzes_path(),[]) if q["id"]!=qid])
    p=quiz_answers_path(qid)
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/<qid>/results")
def quiz_results(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quiz=next((q for q in load_json(quizzes_path(),[]) if q["id"]==qid),None)
    if not quiz: return redirect(url_for("teacher_dashboard"))
    answers=load_json(quiz_answers_path(qid),{})
    not_submitted=[n for n in range(1,STUDENT_COUNT+1) if str(n) not in answers]
    return render_template("quiz_results.html",quiz=quiz,answers=answers,
        total=STUDENT_COUNT,not_submitted=not_submitted)

@app.route("/teacher/word_test/add", methods=["POST"])
def word_test_add():
    if not is_teacher(): return redirect(url_for("index"))
    tests=load_json(word_tests_path(),[])
    title=request.form.get("title","").strip()
    direction=request.form.get("direction","ko_to_en")
    words_raw=request.form.get("words","").strip()
    if not title or not words_raw: return redirect(url_for("teacher_dashboard"))
    words=[]
    for line in words_raw.split("\n"):
        line=line.strip()
        if not line: continue
        sep="," if "," in line else "\t"
        parts=[p.strip() for p in line.split(sep,1)]
        if len(parts)==2 and parts[0] and parts[1]:
            words.append({"ko":parts[0],"en":parts[1]})
    if words:
        wid=datetime.now().strftime("%Y%m%d%H%M%S")
        tests.append({"id":wid,"title":title,"direction":direction,"words":words,
            "active":True,"created":datetime.now().strftime("%m/%d %H:%M")})
        save_json(word_tests_path(),tests)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/from_day", methods=["POST"])
def word_test_from_day():
    if not is_teacher(): return redirect(url_for("index"))
    day=int(request.form.get("day",1))
    direction=request.form.get("direction","ko_to_en")
    words=WORD_DAYS.get(day,[])
    if not words: return redirect(url_for("teacher_dashboard"))
    tests=load_json(word_tests_path(),[])
    wid=datetime.now().strftime("%Y%m%d%H%M%S")
    dir_label={"ko_to_en":"한→영","en_to_ko":"영→한","mixed":"혼합"}.get(direction,"")
    tests.append({"id":wid,"title":f"Day {day} 단어시험 ({dir_label})",
        "direction":direction,"words":words,"active":True,
        "created":datetime.now().strftime("%m/%d %H:%M"),"day":day})
    save_json(word_tests_path(),tests)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/toggle/<wid>")
def word_test_toggle(wid):
    if not is_teacher(): return redirect(url_for("index"))
    tests=load_json(word_tests_path(),[])
    for w in tests:
        if w["id"]==wid: w["active"]=not w.get("active",True)
    save_json(word_tests_path(),tests); return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/delete/<wid>")
def word_test_delete(wid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(word_tests_path(),[w for w in load_json(word_tests_path(),[]) if w["id"]!=wid])
    p=word_answers_path(wid)
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/<wid>/results")
def word_test_results(wid):
    if not is_teacher(): return redirect(url_for("index"))
    tests=load_json(word_tests_path(),[])
    test=next((w for w in tests if w["id"]==wid),None)
    if not test: return redirect(url_for("teacher_dashboard"))
    return render_template("word_test_results.html",test=test,
        answers=load_json(word_answers_path(wid),{}),total=STUDENT_COUNT)

@app.route("/teacher/board/add", methods=["POST"])
def board_add():
    if not is_teacher(): return jsonify({"ok":False})
    data=request.get_json()
    title=data.get("title","").strip()
    if not title: return jsonify({"ok":False,"msg":"제목을 입력해주세요"})
    boards=get_boards()
    bid=datetime.now().strftime("%Y%m%d%H%M%S%f")
    boards.append({"id":bid,"title":title,"open":True,"created":datetime.now().strftime("%m/%d")})
    set_boards(boards)
    return jsonify({"ok":True,"board":boards[-1]})

@app.route("/teacher/board/toggle/<bid>", methods=["POST"])
def board_toggle(bid):
    if not is_teacher(): return jsonify({"ok":False})
    boards=get_boards()
    for b in boards:
        if b["id"]==bid:
            b["open"]=not b.get("open",True)
            set_boards(boards)
            return jsonify({"ok":True,"open":b["open"]})
    return jsonify({"ok":False})

@app.route("/teacher/board/delete/<bid>", methods=["POST"])
def board_delete_board(bid):
    if not is_teacher(): return jsonify({"ok":False})
    boards=[b for b in get_boards() if b["id"]!=bid]
    set_boards(boards)
    p=board_posts_path(bid)
    if os.path.exists(p): os.remove(p)
    return jsonify({"ok":True})

@app.route("/teacher/homework/save", methods=["POST"])
def homework_save():
    if not is_teacher(): return redirect(url_for("index"))
    data=request.get_json()
    items=data.get("items",[])
    current=get_hw_items()
    for i,item in enumerate(current):
        if i<len(items) and items[i].get("name","").strip():
            item["name"]=items[i]["name"].strip()
    save_json(homework_items_path(),current)
    return jsonify({"ok":True})

@app.route("/teacher/homework/reset", methods=["POST"])
def homework_reset():
    if not is_teacher(): return redirect(url_for("index"))
    p=homework_path()
    if os.path.exists(p): os.remove(p)
    return jsonify({"ok":True})

@app.route("/teacher/reset_pw/<int:num>")
def reset_student_pw(num):
    if not is_teacher(): return redirect(url_for("index"))
    pw=load_json(passwords_path(),{}); pw.pop(str(num),None)
    save_json(passwords_path(),pw)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/student/<int:num>")
def student_detail(num):
    if not is_teacher(): return redirect(url_for("index"))
    att_dates=get_all_att_dates()
    att_records={d:{"present":str(num) in load_json(attendance_path(d),{}),
        "time":load_json(attendance_path(d),{}).get(str(num),"")} for d in att_dates}
    uploads=[f for f in sorted(os.listdir(UPLOAD_DIR)) if f.startswith(f"{num}번_")]
    quizzes=load_json(quizzes_path(),[])
    quiz_records=[{"title":q["title"],"data":load_json(quiz_answers_path(q["id"]),{}).get(str(num)),"questions":q["questions"]}
        for q in quizzes if str(num) in load_json(quiz_answers_path(q["id"]),{})]
    exams=load_json(exams_path(),[])
    exam_records=[{"title":e["title"],"data":load_json(exam_answers_path(e["id"]),{}).get(str(num))}
        for e in exams if str(num) in load_json(exam_answers_path(e["id"]),{})]
    word_tests=load_json(word_tests_path(),[])
    wt_records=[{"title":w["title"],"data":load_json(word_answers_path(w["id"]),{}).get(str(num))}
        for w in word_tests if str(num) in load_json(word_answers_path(w["id"]),{})]
    present_count=sum(1 for v in att_records.values() if v["present"])
    return render_template("student_detail.html",num=num,att_records=att_records,
        present_count=present_count,total_days=len(att_dates),uploads=uploads,
        quiz_records=quiz_records,exam_records=exam_records,wt_records=wt_records)

if __name__ == "__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
