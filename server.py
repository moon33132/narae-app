import os, json, csv, random
from datetime import datetime, date
from flask import (Flask, render_template, request, redirect,
    url_for, send_from_directory, jsonify, session, Response)
from werkzeug.utils import secure_filename

WORD_DAYS = {
    1: [
        {'ko': '개', 'en': 'dog'},
        {'ko': '고양이', 'en': 'cat'},
        {'ko': '새', 'en': 'bird'},
        {'ko': '물고기', 'en': 'fish'},
        {'ko': '토끼', 'en': 'rabbit'},
        {'ko': '말', 'en': 'horse'},
        {'ko': '소', 'en': 'cow'},
        {'ko': '돼지', 'en': 'pig'},
        {'ko': '닭', 'en': 'chicken'},
        {'ko': '오리', 'en': 'duck'},
        {'ko': '개구리', 'en': 'frog'},
        {'ko': '곰', 'en': 'bear'},
        {'ko': '사자', 'en': 'lion'},
        {'ko': '호랑이', 'en': 'tiger'},
        {'ko': '코끼리', 'en': 'elephant'},
        {'ko': '원숭이', 'en': 'monkey'},
        {'ko': '뱀', 'en': 'snake'},
        {'ko': '쥐', 'en': 'mouse'},
        {'ko': '양', 'en': 'sheep'},
        {'ko': '여우', 'en': 'fox'},
    ],
    2: [
        {'ko': '사과', 'en': 'apple'},
        {'ko': '바나나', 'en': 'banana'},
        {'ko': '오렌지', 'en': 'orange'},
        {'ko': '포도', 'en': 'grape'},
        {'ko': '멜론', 'en': 'melon'},
        {'ko': '복숭아', 'en': 'peach'},
        {'ko': '딸기', 'en': 'strawberry'},
        {'ko': '체리', 'en': 'cherry'},
        {'ko': '레몬', 'en': 'lemon'},
        {'ko': '토마토', 'en': 'tomato'},
        {'ko': '감자', 'en': 'potato'},
        {'ko': '당근', 'en': 'carrot'},
        {'ko': '양파', 'en': 'onion'},
        {'ko': '옥수수', 'en': 'corn'},
        {'ko': '쌀', 'en': 'rice'},
        {'ko': '빵', 'en': 'bread'},
        {'ko': '치즈', 'en': 'cheese'},
        {'ko': '달걀', 'en': 'egg'},
        {'ko': '우유', 'en': 'milk'},
        {'ko': '물', 'en': 'water'},
    ],
    3: [
        {'ko': '엄마', 'en': 'mother'},
        {'ko': '아빠', 'en': 'father'},
        {'ko': '언니/누나', 'en': 'sister'},
        {'ko': '오빠/형', 'en': 'brother'},
        {'ko': '아기', 'en': 'baby'},
        {'ko': '할머니', 'en': 'grandmother'},
        {'ko': '할아버지', 'en': 'grandfather'},
        {'ko': '삼촌', 'en': 'uncle'},
        {'ko': '이모/고모', 'en': 'aunt'},
        {'ko': '사촌', 'en': 'cousin'},
        {'ko': '친구', 'en': 'friend'},
        {'ko': '선생님', 'en': 'teacher'},
        {'ko': '학생', 'en': 'student'},
        {'ko': '의사', 'en': 'doctor'},
        {'ko': '간호사', 'en': 'nurse'},
        {'ko': '경찰', 'en': 'police'},
        {'ko': '소방관', 'en': 'firefighter'},
        {'ko': '운전사', 'en': 'driver'},
        {'ko': '농부', 'en': 'farmer'},
        {'ko': '요리사', 'en': 'cook'},
    ],
    4: [
        {'ko': '머리', 'en': 'head'},
        {'ko': '머리카락', 'en': 'hair'},
        {'ko': '얼굴', 'en': 'face'},
        {'ko': '눈', 'en': 'eye'},
        {'ko': '귀', 'en': 'ear'},
        {'ko': '코', 'en': 'nose'},
        {'ko': '입', 'en': 'mouth'},
        {'ko': '이빨', 'en': 'tooth'},
        {'ko': '손', 'en': 'hand'},
        {'ko': '손가락', 'en': 'finger'},
        {'ko': '팔', 'en': 'arm'},
        {'ko': '다리', 'en': 'leg'},
        {'ko': '발', 'en': 'foot'},
        {'ko': '무릎', 'en': 'knee'},
        {'ko': '어깨', 'en': 'shoulder'},
        {'ko': '목', 'en': 'neck'},
        {'ko': '등', 'en': 'back'},
        {'ko': '배', 'en': 'stomach'},
        {'ko': '심장', 'en': 'heart'},
        {'ko': '뼈', 'en': 'bone'},
    ],
    5: [
        {'ko': '빨간', 'en': 'red'},
        {'ko': '파란', 'en': 'blue'},
        {'ko': '노란', 'en': 'yellow'},
        {'ko': '초록', 'en': 'green'},
        {'ko': '하얀', 'en': 'white'},
        {'ko': '검은', 'en': 'black'},
        {'ko': '분홍', 'en': 'pink'},
        {'ko': '보라', 'en': 'purple'},
        {'ko': '갈색', 'en': 'brown'},
        {'ko': '회색', 'en': 'gray'},
        {'ko': '큰', 'en': 'big'},
        {'ko': '작은', 'en': 'small'},
        {'ko': '긴', 'en': 'long'},
        {'ko': '짧은', 'en': 'short'},
        {'ko': '키 큰', 'en': 'tall'},
        {'ko': '빠른', 'en': 'fast'},
        {'ko': '느린', 'en': 'slow'},
        {'ko': '무거운', 'en': 'heavy'},
        {'ko': '가벼운', 'en': 'light'},
        {'ko': '강한', 'en': 'strong'},
    ],
    6: [
        {'ko': '행복한', 'en': 'happy'},
        {'ko': '슬픈', 'en': 'sad'},
        {'ko': '화난', 'en': 'angry'},
        {'ko': '피곤한', 'en': 'tired'},
        {'ko': '배고픈', 'en': 'hungry'},
        {'ko': '목마른', 'en': 'thirsty'},
        {'ko': '아픈', 'en': 'sick'},
        {'ko': '무서운', 'en': 'scared'},
        {'ko': '용감한', 'en': 'brave'},
        {'ko': '친절한', 'en': 'kind'},
        {'ko': '재미있는', 'en': 'funny'},
        {'ko': '조용한', 'en': 'quiet'},
        {'ko': '시끄러운', 'en': 'loud'},
        {'ko': '깨끗한', 'en': 'clean'},
        {'ko': '더러운', 'en': 'dirty'},
        {'ko': '뜨거운', 'en': 'hot'},
        {'ko': '차가운', 'en': 'cold'},
        {'ko': '새로운', 'en': 'new'},
        {'ko': '오래된', 'en': 'old'},
        {'ko': '예쁜', 'en': 'pretty'},
    ],
    7: [
        {'ko': '학교', 'en': 'school'},
        {'ko': '교실', 'en': 'classroom'},
        {'ko': '책상', 'en': 'desk'},
        {'ko': '의자', 'en': 'chair'},
        {'ko': '책', 'en': 'book'},
        {'ko': '연필', 'en': 'pencil'},
        {'ko': '지우개', 'en': 'eraser'},
        {'ko': '자', 'en': 'ruler'},
        {'ko': '공책', 'en': 'notebook'},
        {'ko': '가방', 'en': 'bag'},
        {'ko': '숙제', 'en': 'homework'},
        {'ko': '시험', 'en': 'test'},
        {'ko': '질문', 'en': 'question'},
        {'ko': '대답', 'en': 'answer'},
        {'ko': '수업', 'en': 'lesson'},
        {'ko': '수학', 'en': 'math'},
        {'ko': '과학', 'en': 'science'},
        {'ko': '음악', 'en': 'music'},
        {'ko': '미술', 'en': 'art'},
        {'ko': '운동', 'en': 'sport'},
    ],
    8: [
        {'ko': '집', 'en': 'house'},
        {'ko': '방', 'en': 'room'},
        {'ko': '부엌', 'en': 'kitchen'},
        {'ko': '화장실', 'en': 'bathroom'},
        {'ko': '침실', 'en': 'bedroom'},
        {'ko': '문', 'en': 'door'},
        {'ko': '창문', 'en': 'window'},
        {'ko': '벽', 'en': 'wall'},
        {'ko': '바닥', 'en': 'floor'},
        {'ko': '지붕', 'en': 'roof'},
        {'ko': '정원', 'en': 'garden'},
        {'ko': '탁자', 'en': 'table'},
        {'ko': '침대', 'en': 'bed'},
        {'ko': '소파', 'en': 'sofa'},
        {'ko': '전등', 'en': 'lamp'},
        {'ko': '시계', 'en': 'clock'},
        {'ko': '거울', 'en': 'mirror'},
        {'ko': '열쇠', 'en': 'key'},
        {'ko': '계단', 'en': 'stairs'},
        {'ko': '전화기', 'en': 'telephone'},
    ],
    9: [
        {'ko': '셔츠', 'en': 'shirt'},
        {'ko': '바지', 'en': 'pants'},
        {'ko': '원피스', 'en': 'dress'},
        {'ko': '치마', 'en': 'skirt'},
        {'ko': '재킷', 'en': 'jacket'},
        {'ko': '코트', 'en': 'coat'},
        {'ko': '모자', 'en': 'hat'},
        {'ko': '신발', 'en': 'shoes'},
        {'ko': '양말', 'en': 'socks'},
        {'ko': '장갑', 'en': 'gloves'},
        {'ko': '목도리', 'en': 'scarf'},
        {'ko': '우산', 'en': 'umbrella'},
        {'ko': '안경', 'en': 'glasses'},
        {'ko': '시계', 'en': 'watch'},
        {'ko': '반지', 'en': 'ring'},
        {'ko': '주머니', 'en': 'pocket'},
        {'ko': '단추', 'en': 'button'},
        {'ko': '지퍼', 'en': 'zipper'},
        {'ko': '부츠', 'en': 'boots'},
        {'ko': '교복', 'en': 'uniform'},
    ],
    10: [
        {'ko': '아침', 'en': 'morning'},
        {'ko': '오후', 'en': 'afternoon'},
        {'ko': '저녁', 'en': 'evening'},
        {'ko': '밤', 'en': 'night'},
        {'ko': '오늘', 'en': 'today'},
        {'ko': '내일', 'en': 'tomorrow'},
        {'ko': '어제', 'en': 'yesterday'},
        {'ko': '주', 'en': 'week'},
        {'ko': '달', 'en': 'month'},
        {'ko': '해/년', 'en': 'year'},
        {'ko': '봄', 'en': 'spring'},
        {'ko': '여름', 'en': 'summer'},
        {'ko': '가을', 'en': 'fall'},
        {'ko': '겨울', 'en': 'winter'},
        {'ko': '일요일', 'en': 'Sunday'},
        {'ko': '월요일', 'en': 'Monday'},
        {'ko': '화요일', 'en': 'Tuesday'},
        {'ko': '수요일', 'en': 'Wednesday'},
        {'ko': '목요일', 'en': 'Thursday'},
        {'ko': '금요일', 'en': 'Friday'},
    ],
    11: [
        {'ko': '태양', 'en': 'sun'},
        {'ko': '달', 'en': 'moon'},
        {'ko': '별', 'en': 'star'},
        {'ko': '구름', 'en': 'cloud'},
        {'ko': '비', 'en': 'rain'},
        {'ko': '눈', 'en': 'snow'},
        {'ko': '바람', 'en': 'wind'},
        {'ko': '하늘', 'en': 'sky'},
        {'ko': '무지개', 'en': 'rainbow'},
        {'ko': '천둥', 'en': 'thunder'},
        {'ko': '나무', 'en': 'tree'},
        {'ko': '꽃', 'en': 'flower'},
        {'ko': '풀/잔디', 'en': 'grass'},
        {'ko': '잎', 'en': 'leaf'},
        {'ko': '강', 'en': 'river'},
        {'ko': '호수', 'en': 'lake'},
        {'ko': '산', 'en': 'mountain'},
        {'ko': '바다', 'en': 'sea'},
        {'ko': '섬', 'en': 'island'},
        {'ko': '숲', 'en': 'forest'},
    ],
    12: [
        {'ko': '먹다', 'en': 'eat'},
        {'ko': '마시다', 'en': 'drink'},
        {'ko': '달리다', 'en': 'run'},
        {'ko': '걷다', 'en': 'walk'},
        {'ko': '점프하다', 'en': 'jump'},
        {'ko': '수영하다', 'en': 'swim'},
        {'ko': '자다', 'en': 'sleep'},
        {'ko': '일어나다', 'en': 'wake'},
        {'ko': '앉다', 'en': 'sit'},
        {'ko': '서다', 'en': 'stand'},
        {'ko': '열다', 'en': 'open'},
        {'ko': '닫다', 'en': 'close'},
        {'ko': '밀다', 'en': 'push'},
        {'ko': '당기다', 'en': 'pull'},
        {'ko': '주다', 'en': 'give'},
        {'ko': '가져가다', 'en': 'take'},
        {'ko': '오다', 'en': 'come'},
        {'ko': '가다', 'en': 'go'},
        {'ko': '멈추다', 'en': 'stop'},
        {'ko': '시작하다', 'en': 'start'},
    ],
    13: [
        {'ko': '읽다', 'en': 'read'},
        {'ko': '쓰다', 'en': 'write'},
        {'ko': '말하다', 'en': 'speak'},
        {'ko': '듣다', 'en': 'listen'},
        {'ko': '노래하다', 'en': 'sing'},
        {'ko': '춤추다', 'en': 'dance'},
        {'ko': '그리다', 'en': 'draw'},
        {'ko': '놀다', 'en': 'play'},
        {'ko': '공부하다', 'en': 'study'},
        {'ko': '생각하다', 'en': 'think'},
        {'ko': '알다', 'en': 'know'},
        {'ko': '배우다', 'en': 'learn'},
        {'ko': '가르치다', 'en': 'teach'},
        {'ko': '돕다', 'en': 'help'},
        {'ko': '시도하다', 'en': 'try'},
        {'ko': '원하다', 'en': 'want'},
        {'ko': '필요하다', 'en': 'need'},
        {'ko': '좋아하다', 'en': 'like'},
        {'ko': '사랑하다', 'en': 'love'},
        {'ko': '바라다', 'en': 'hope'},
    ],
    14: [
        {'ko': '보다', 'en': 'look'},
        {'ko': '보이다', 'en': 'see'},
        {'ko': '들리다', 'en': 'hear'},
        {'ko': '냄새맡다', 'en': 'smell'},
        {'ko': '만지다', 'en': 'touch'},
        {'ko': '느끼다', 'en': 'feel'},
        {'ko': '웃다', 'en': 'laugh'},
        {'ko': '울다', 'en': 'cry'},
        {'ko': '미소짓다', 'en': 'smile'},
        {'ko': '소리치다', 'en': 'shout'},
        {'ko': '씻다', 'en': 'wash'},
        {'ko': '닦다', 'en': 'brush'},
        {'ko': '요리하다', 'en': 'cook'},
        {'ko': '자르다', 'en': 'cut'},
        {'ko': '섞다', 'en': 'mix'},
        {'ko': '던지다', 'en': 'throw'},
        {'ko': '잡다', 'en': 'catch'},
        {'ko': '차다', 'en': 'kick'},
        {'ko': '치다', 'en': 'hit'},
        {'ko': '나르다', 'en': 'carry'},
    ],
    15: [
        {'ko': '하나', 'en': 'one'},
        {'ko': '둘', 'en': 'two'},
        {'ko': '셋', 'en': 'three'},
        {'ko': '넷', 'en': 'four'},
        {'ko': '다섯', 'en': 'five'},
        {'ko': '여섯', 'en': 'six'},
        {'ko': '일곱', 'en': 'seven'},
        {'ko': '여덟', 'en': 'eight'},
        {'ko': '아홉', 'en': 'nine'},
        {'ko': '열', 'en': 'ten'},
        {'ko': '스물', 'en': 'twenty'},
        {'ko': '서른', 'en': 'thirty'},
        {'ko': '쉰', 'en': 'fifty'},
        {'ko': '백', 'en': 'hundred'},
        {'ko': '천', 'en': 'thousand'},
        {'ko': '첫 번째', 'en': 'first'},
        {'ko': '두 번째', 'en': 'second'},
        {'ko': '세 번째', 'en': 'third'},
        {'ko': '마지막', 'en': 'last'},
        {'ko': '다음', 'en': 'next'},
    ],
    16: [
        {'ko': '아침식사', 'en': 'breakfast'},
        {'ko': '점심', 'en': 'lunch'},
        {'ko': '저녁식사', 'en': 'dinner'},
        {'ko': '간식', 'en': 'snack'},
        {'ko': '국', 'en': 'soup'},
        {'ko': '샐러드', 'en': 'salad'},
        {'ko': '피자', 'en': 'pizza'},
        {'ko': '샌드위치', 'en': 'sandwich'},
        {'ko': '국수', 'en': 'noodle'},
        {'ko': '케이크', 'en': 'cake'},
        {'ko': '쿠키', 'en': 'cookie'},
        {'ko': '사탕', 'en': 'candy'},
        {'ko': '아이스크림', 'en': 'ice cream'},
        {'ko': '주스', 'en': 'juice'},
        {'ko': '차', 'en': 'tea'},
        {'ko': '설탕', 'en': 'sugar'},
        {'ko': '소금', 'en': 'salt'},
        {'ko': '버터', 'en': 'butter'},
        {'ko': '숟가락', 'en': 'spoon'},
        {'ko': '포크', 'en': 'fork'},
    ],
    17: [
        {'ko': '자동차', 'en': 'car'},
        {'ko': '버스', 'en': 'bus'},
        {'ko': '기차', 'en': 'train'},
        {'ko': '비행기', 'en': 'airplane'},
        {'ko': '자전거', 'en': 'bicycle'},
        {'ko': '배', 'en': 'ship'},
        {'ko': '택시', 'en': 'taxi'},
        {'ko': '지하철', 'en': 'subway'},
        {'ko': '도로', 'en': 'road'},
        {'ko': '다리', 'en': 'bridge'},
        {'ko': '역', 'en': 'station'},
        {'ko': '공항', 'en': 'airport'},
        {'ko': '표', 'en': 'ticket'},
        {'ko': '지도', 'en': 'map'},
        {'ko': '왼쪽', 'en': 'left'},
        {'ko': '오른쪽', 'en': 'right'},
        {'ko': '직진', 'en': 'straight'},
        {'ko': '모퉁이', 'en': 'corner'},
        {'ko': '건너다', 'en': 'cross'},
        {'ko': '돌다', 'en': 'turn'},
    ],
    18: [
        {'ko': '공원', 'en': 'park'},
        {'ko': '병원', 'en': 'hospital'},
        {'ko': '도서관', 'en': 'library'},
        {'ko': '박물관', 'en': 'museum'},
        {'ko': '가게', 'en': 'store'},
        {'ko': '시장', 'en': 'market'},
        {'ko': '은행', 'en': 'bank'},
        {'ko': '교회', 'en': 'church'},
        {'ko': '식당', 'en': 'restaurant'},
        {'ko': '호텔', 'en': 'hotel'},
        {'ko': '극장', 'en': 'theater'},
        {'ko': '동물원', 'en': 'zoo'},
        {'ko': '농장', 'en': 'farm'},
        {'ko': '해변', 'en': 'beach'},
        {'ko': '캠프', 'en': 'camp'},
        {'ko': '놀이터', 'en': 'playground'},
        {'ko': '수영장', 'en': 'pool'},
        {'ko': '체육관', 'en': 'gym'},
        {'ko': '경기장', 'en': 'stadium'},
        {'ko': '성', 'en': 'castle'},
    ],
    19: [
        {'ko': '축구', 'en': 'soccer'},
        {'ko': '야구', 'en': 'baseball'},
        {'ko': '농구', 'en': 'basketball'},
        {'ko': '테니스', 'en': 'tennis'},
        {'ko': '수영', 'en': 'swimming'},
        {'ko': '달리기', 'en': 'running'},
        {'ko': '스케이트', 'en': 'skating'},
        {'ko': '스키', 'en': 'skiing'},
        {'ko': '등산', 'en': 'hiking'},
        {'ko': '캠핑', 'en': 'camping'},
        {'ko': '게임', 'en': 'game'},
        {'ko': '팀', 'en': 'team'},
        {'ko': '선수', 'en': 'player'},
        {'ko': '승자', 'en': 'winner'},
        {'ko': '패자', 'en': 'loser'},
        {'ko': '점수', 'en': 'score'},
        {'ko': '골/목표', 'en': 'goal'},
        {'ko': '경주', 'en': 'race'},
        {'ko': '경기', 'en': 'match'},
        {'ko': '상', 'en': 'prize'},
    ],
    20: [
        {'ko': '컴퓨터', 'en': 'computer'},
        {'ko': '전화기', 'en': 'phone'},
        {'ko': '카메라', 'en': 'camera'},
        {'ko': '화면', 'en': 'screen'},
        {'ko': '키보드', 'en': 'keyboard'},
        {'ko': '마우스', 'en': 'mouse'},
        {'ko': '영상', 'en': 'video'},
        {'ko': '사진', 'en': 'photo'},
        {'ko': '메시지', 'en': 'message'},
        {'ko': '이메일', 'en': 'email'},
        {'ko': '인터넷', 'en': 'internet'},
        {'ko': '웹사이트', 'en': 'website'},
        {'ko': '비밀번호', 'en': 'password'},
        {'ko': '로봇', 'en': 'robot'},
        {'ko': '게임', 'en': 'game'},
        {'ko': '프린터', 'en': 'printer'},
        {'ko': '스피커', 'en': 'speaker'},
        {'ko': '배터리', 'en': 'battery'},
        {'ko': '충전기', 'en': 'charger'},
        {'ko': '프로그램', 'en': 'program'},
    ],
    21: [
        {'ko': '나라', 'en': 'country'},
        {'ko': '도시', 'en': 'city'},
        {'ko': '마을', 'en': 'town'},
        {'ko': '거리', 'en': 'street'},
        {'ko': '건물', 'en': 'building'},
        {'ko': '깃발', 'en': 'flag'},
        {'ko': '왕', 'en': 'king'},
        {'ko': '여왕', 'en': 'queen'},
        {'ko': '대통령', 'en': 'president'},
        {'ko': '군인', 'en': 'soldier'},
        {'ko': '평화', 'en': 'peace'},
        {'ko': '전쟁', 'en': 'war'},
        {'ko': '규칙', 'en': 'rule'},
        {'ko': '법', 'en': 'law'},
        {'ko': '투표', 'en': 'vote'},
        {'ko': '무리/그룹', 'en': 'group'},
        {'ko': '지도자', 'en': 'leader'},
        {'ko': '회원', 'en': 'member'},
        {'ko': '모임', 'en': 'meeting'},
        {'ko': '뉴스', 'en': 'news'},
    ],
    22: [
        {'ko': '생일', 'en': 'birthday'},
        {'ko': '파티', 'en': 'party'},
        {'ko': '선물', 'en': 'present'},
        {'ko': '휴일', 'en': 'holiday'},
        {'ko': '방학', 'en': 'vacation'},
        {'ko': '축제', 'en': 'festival'},
        {'ko': '결혼식', 'en': 'wedding'},
        {'ko': '카드', 'en': 'card'},
        {'ko': '풍선', 'en': 'balloon'},
        {'ko': '초', 'en': 'candle'},
        {'ko': '노래', 'en': 'song'},
        {'ko': '춤', 'en': 'dance'},
        {'ko': '영화', 'en': 'movie'},
        {'ko': '공연', 'en': 'show'},
        {'ko': '콘서트', 'en': 'concert'},
        {'ko': '그림', 'en': 'picture'},
        {'ko': '이야기', 'en': 'story'},
        {'ko': '취미', 'en': 'hobby'},
        {'ko': '꿈', 'en': 'dream'},
        {'ko': '소원', 'en': 'wish'},
    ],
    23: [
        {'ko': '돈', 'en': 'money'},
        {'ko': '동전', 'en': 'coin'},
        {'ko': '가격', 'en': 'price'},
        {'ko': '싼', 'en': 'cheap'},
        {'ko': '비싼', 'en': 'expensive'},
        {'ko': '사다', 'en': 'buy'},
        {'ko': '팔다', 'en': 'sell'},
        {'ko': '지불하다', 'en': 'pay'},
        {'ko': '무료의', 'en': 'free'},
        {'ko': '가게', 'en': 'shop'},
        {'ko': '장난감', 'en': 'toy'},
        {'ko': '인형', 'en': 'doll'},
        {'ko': '공', 'en': 'ball'},
        {'ko': '연', 'en': 'kite'},
        {'ko': '퍼즐', 'en': 'puzzle'},
        {'ko': '로봇', 'en': 'robot'},
        {'ko': '블록', 'en': 'block'},
        {'ko': '보드', 'en': 'board'},
        {'ko': '카드', 'en': 'card'},
        {'ko': '상품', 'en': 'prize'},
    ],
    24: [
        {'ko': '안녕', 'en': 'hello'},
        {'ko': '잘 가', 'en': 'goodbye'},
        {'ko': '제발', 'en': 'please'},
        {'ko': '미안해', 'en': 'sorry'},
        {'ko': '고마워', 'en': 'thank you'},
        {'ko': '실례합니다', 'en': 'excuse me'},
        {'ko': '환영해', 'en': 'welcome'},
        {'ko': '네', 'en': 'yes'},
        {'ko': '아니오', 'en': 'no'},
        {'ko': '아마도', 'en': 'maybe'},
        {'ko': '항상', 'en': 'always'},
        {'ko': '절대 안', 'en': 'never'},
        {'ko': '자주', 'en': 'often'},
        {'ko': '가끔', 'en': 'sometimes'},
        {'ko': '다시', 'en': 'again'},
        {'ko': '함께', 'en': 'together'},
        {'ko': '혼자', 'en': 'alone'},
        {'ko': '이미', 'en': 'already'},
        {'ko': '곧', 'en': 'soon'},
        {'ko': '여전히', 'en': 'still'},
    ],
    25: [
        {'ko': '여기', 'en': 'here'},
        {'ko': '저기', 'en': 'there'},
        {'ko': '위', 'en': 'up'},
        {'ko': '아래', 'en': 'down'},
        {'ko': '안', 'en': 'inside'},
        {'ko': '밖', 'en': 'outside'},
        {'ko': '앞', 'en': 'front'},
        {'ko': '뒤', 'en': 'behind'},
        {'ko': '사이', 'en': 'between'},
        {'ko': '옆', 'en': 'beside'},
        {'ko': '가까운', 'en': 'near'},
        {'ko': '먼', 'en': 'far'},
        {'ko': '위에', 'en': 'above'},
        {'ko': '아래에', 'en': 'below'},
        {'ko': '주위에', 'en': 'around'},
        {'ko': '건너편', 'en': 'across'},
        {'ko': '통해서', 'en': 'through'},
        {'ko': '쪽으로', 'en': 'toward'},
        {'ko': '멀리', 'en': 'away'},
        {'ko': '따라서', 'en': 'along'},
    ],
    26: [
        {'ko': '지구', 'en': 'earth'},
        {'ko': '우주', 'en': 'space'},
        {'ko': '행성', 'en': 'planet'},
        {'ko': '로켓', 'en': 'rocket'},
        {'ko': '공기', 'en': 'air'},
        {'ko': '불', 'en': 'fire'},
        {'ko': '얼음', 'en': 'ice'},
        {'ko': '바위', 'en': 'rock'},
        {'ko': '모래', 'en': 'sand'},
        {'ko': '진흙', 'en': 'mud'},
        {'ko': '기름', 'en': 'oil'},
        {'ko': '금', 'en': 'gold'},
        {'ko': '은', 'en': 'silver'},
        {'ko': '철', 'en': 'iron'},
        {'ko': '나무(재료)', 'en': 'wood'},
        {'ko': '종이', 'en': 'paper'},
        {'ko': '유리', 'en': 'glass'},
        {'ko': '플라스틱', 'en': 'plastic'},
        {'ko': '면', 'en': 'cotton'},
        {'ko': '고무', 'en': 'rubber'},
    ],
    27: [
        {'ko': '가지다', 'en': 'have'},
        {'ko': '만들다', 'en': 'make'},
        {'ko': '찾다', 'en': 'find'},
        {'ko': '잃다', 'en': 'lose'},
        {'ko': '간직하다', 'en': 'keep'},
        {'ko': '가져오다', 'en': 'bring'},
        {'ko': '보내다', 'en': 'send'},
        {'ko': '짓다', 'en': 'build'},
        {'ko': '부수다', 'en': 'break'},
        {'ko': '고치다', 'en': 'fix'},
        {'ko': '선택하다', 'en': 'choose'},
        {'ko': '바꾸다', 'en': 'change'},
        {'ko': '나누다', 'en': 'share'},
        {'ko': '기다리다', 'en': 'wait'},
        {'ko': '따라가다', 'en': 'follow'},
        {'ko': '움직이다', 'en': 'move'},
        {'ko': '숨다', 'en': 'hide'},
        {'ko': '오르다', 'en': 'climb'},
        {'ko': '날다', 'en': 'fly'},
        {'ko': '떨어지다', 'en': 'fall'},
    ],
    28: [
        {'ko': '믿다', 'en': 'believe'},
        {'ko': '기억하다', 'en': 'remember'},
        {'ko': '잊다', 'en': 'forget'},
        {'ko': '이해하다', 'en': 'understand'},
        {'ko': '동의하다', 'en': 'agree'},
        {'ko': '결정하다', 'en': 'decide'},
        {'ko': '약속하다', 'en': 'promise'},
        {'ko': '설명하다', 'en': 'explain'},
        {'ko': '연습하다', 'en': 'practice'},
        {'ko': '준비하다', 'en': 'prepare'},
        {'ko': '시작하다', 'en': 'begin'},
        {'ko': '끝내다', 'en': 'finish'},
        {'ko': '즐기다', 'en': 'enjoy'},
        {'ko': '걱정하다', 'en': 'worry'},
        {'ko': '궁금하다', 'en': 'wonder'},
        {'ko': '추측하다', 'en': 'guess'},
        {'ko': '그리워하다', 'en': 'miss'},
        {'ko': '저축하다', 'en': 'save'},
        {'ko': '쓰다(돈)', 'en': 'spend'},
        {'ko': '빌리다', 'en': 'borrow'},
    ],
    29: [
        {'ko': '같은', 'en': 'same'},
        {'ko': '다른', 'en': 'different'},
        {'ko': '쉬운', 'en': 'easy'},
        {'ko': '어려운', 'en': 'difficult'},
        {'ko': '중요한', 'en': 'important'},
        {'ko': '흥미로운', 'en': 'interesting'},
        {'ko': '지루한', 'en': 'boring'},
        {'ko': '위험한', 'en': 'dangerous'},
        {'ko': '안전한', 'en': 'safe'},
        {'ko': '인기 있는', 'en': 'popular'},
        {'ko': '유명한', 'en': 'famous'},
        {'ko': '특별한', 'en': 'special'},
        {'ko': '가장 좋아하는', 'en': 'favorite'},
        {'ko': '가능한', 'en': 'possible'},
        {'ko': '준비된', 'en': 'ready'},
        {'ko': '바쁜', 'en': 'busy'},
        {'ko': '게으른', 'en': 'lazy'},
        {'ko': '조심하는', 'en': 'careful'},
        {'ko': '놀란', 'en': 'surprised'},
        {'ko': '자랑스러운', 'en': 'proud'},
    ],
    30: [
        {'ko': '세계', 'en': 'world'},
        {'ko': '사람들', 'en': 'people'},
        {'ko': '삶', 'en': 'life'},
        {'ko': '시간', 'en': 'time'},
        {'ko': '생각', 'en': 'idea'},
        {'ko': '계획', 'en': 'plan'},
        {'ko': '문제', 'en': 'problem'},
        {'ko': '이유', 'en': 'reason'},
        {'ko': '예시', 'en': 'example'},
        {'ko': '기회', 'en': 'chance'},
        {'ko': '미래', 'en': 'future'},
        {'ko': '역사', 'en': 'history'},
        {'ko': '자연', 'en': 'nature'},
        {'ko': '문화', 'en': 'culture'},
        {'ko': '건강', 'en': 'health'},
        {'ko': '에너지', 'en': 'energy'},
        {'ko': '힘', 'en': 'power'},
        {'ko': '성공', 'en': 'success'},
        {'ko': '실수', 'en': 'mistake'},
        {'ko': '경험', 'en': 'experience'},
    ],
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "narae2025secret")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400 * 30  # 30일
app.jinja_env.filters['enumerate'] = enumerate

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
SHARE_DIR  = os.path.join(BASE_DIR, "shared")
DATA_DIR   = os.path.join(BASE_DIR, "data")
ALLOWED_EXT = {"pdf","hwp","hwpx","docx","xlsx","pptx","jpg","jpeg","png","gif","mp4","mp3","txt","zip"}
STUDENT_COUNT = 22
TEACHER_PW = os.environ.get("TEACHER_PW", "narae1234")

for d in [UPLOAD_DIR, SHARE_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# ── 헬퍼 ──────────────────────────────────────────
def allowed(f): return "." in f and f.rsplit(".",1)[1].lower() in ALLOWED_EXT
def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f: return json.load(f)
    return default
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

def passwords_path():    return os.path.join(DATA_DIR, "passwords.json")
def attendance_path(d=None):
    d = d or date.today().isoformat()
    return os.path.join(DATA_DIR, f"attendance_{d}.json")
def notices_path():      return os.path.join(DATA_DIR, "notices.json")
def notices_path():       return os.path.join(DATA_DIR, "notices.json")
def quiz_path():         return os.path.join(DATA_DIR, "quizzes.json")
def quiz_answers_path(qid): return os.path.join(DATA_DIR, f"answers_{qid}.json")
def exams_path():        return os.path.join(DATA_DIR, "exams.json")
def exam_answers_path(eid): return os.path.join(DATA_DIR, f"exam_answers_{eid}.json")
def word_tests_path():   return os.path.join(DATA_DIR, "word_tests.json")
def word_answers_path(wid): return os.path.join(DATA_DIR, f"word_answers_{wid}.json")
def homework_path():     return os.path.join(DATA_DIR, f"homework_{date.today()}.json")
def study_topics_path(): return os.path.join(DATA_DIR, "study_topics.json")
def homework_items_path(): return os.path.join(DATA_DIR, "homework_items.json")

DEFAULT_HW_ITEMS = [
    {"id": "hw_1", "name": "수학 숙제"},
    {"id": "hw_2", "name": "국어 숙제"},
    {"id": "hw_3", "name": "알림장"},
]

def get_hw_items():
    items = load_json(homework_items_path(), [])
    if not items:
        # 파일 없거나 비어있으면 기본값 저장 후 반환
        save_json(homework_items_path(), DEFAULT_HW_ITEMS)
        return list(DEFAULT_HW_ITEMS)
    # id가 없는 항목 보정 (구버전 데이터 호환)
    for i, item in enumerate(items):
        if "id" not in item:
            item["id"] = f"hw_{i+1}"
    return items
def boards_path():         return os.path.join(DATA_DIR, "boards.json")   # 게시판 목록
def board_posts_path(bid): return os.path.join(DATA_DIR, f"board_{bid}.json")  # 게시판별 글
BOARD_UPLOAD_DIR = os.path.join(BASE_DIR, "board_uploads")
os.makedirs(BOARD_UPLOAD_DIR, exist_ok=True)

# 게시판 목록 메모리 캐시
_boards_cache = None

def get_boards():
    global _boards_cache
    if _boards_cache is None:
        _boards_cache = load_json(boards_path(), [])
    return _boards_cache

def set_boards(boards):
    global _boards_cache
    _boards_cache = boards
    save_json(boards_path(), boards)

def get_board(bid):
    return next((b for b in get_boards() if b["id"] == bid), None)
BOARD_UPLOAD_DIR = os.path.join(BASE_DIR, "board_uploads")
os.makedirs(BOARD_UPLOAD_DIR, exist_ok=True)

def is_teacher():        return session.get("role") == "teacher"
def get_student_num():   return session.get("student_num")
def today_str():         return date.today().strftime("%Y년 %m월 %d일")

def record_attendance(num):
    att = load_json(attendance_path(), {})
    if str(num) not in att:
        att[str(num)] = datetime.now().strftime("%H:%M:%S")
        save_json(attendance_path(), att)

def get_all_attendance_dates():
    return sorted([f.replace("attendance_","").replace(".json","")
                   for f in os.listdir(DATA_DIR)
                   if f.startswith("attendance_") and f.endswith(".json")])

# ══════════════════════════════════════════════════
# 로그인
# ══════════════════════════════════════════════════
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
                passwords[key] = pw
                save_json(passwords_path(), passwords)
                session.update({"role":"student","student_num":num})
                record_attendance(num)
                return redirect(url_for("student_dashboard"))
            return render_template("register.html", num=num, error="숫자 4자리로 입력해주세요.")
        if pw == "": return render_template("index.html", student_count=STUDENT_COUNT, need_pw=num)
        if passwords[key] == pw:
            session.permanent = True
            session.update({"role":"student","student_num":num})
            record_attendance(num)
            return redirect(url_for("student_dashboard"))
        return render_template("index.html", student_count=STUDENT_COUNT, error="비밀번호가 틀렸어요.", need_pw=num)
    return redirect(url_for("index"))

@app.route("/register", methods=["POST"])
def register():
    try: num = int(request.form.get("num","")); assert 1 <= num <= STUDENT_COUNT
    except: return redirect(url_for("index"))
    pw = request.form.get("new_pw","").strip()
    if len(pw)!=4 or not pw.isdigit():
        return render_template("register.html", num=num, error="숫자 4자리로 입력해주세요.")
    passwords = load_json(passwords_path(), {})
    passwords[str(num)] = pw
    save_json(passwords_path(), passwords)
    session.update({"role":"student","student_num":num})
    record_attendance(num)
    return redirect(url_for("student_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ══════════════════════════════════════════════════
# 학생 대시보드
# ══════════════════════════════════════════════════
@app.route("/student")
def student_dashboard():
    num = get_student_num()
    if not num: return redirect(url_for("index"))
    quizzes        = [q for q in load_json(quiz_path(), []) if q.get("active")]
    exams          = load_json(exams_path(), [])
    active_exams   = [e for e in exams if e.get("active")]
    word_tests     = load_json(word_tests_path(), [])
    active_wt      = [w for w in word_tests if w.get("active")]
    shared_files   = sorted(os.listdir(SHARE_DIR))
    submitted_exams = {e["id"] for e in exams if str(num) in load_json(exam_answers_path(e["id"]),{})}
    submitted_wt    = {w["id"] for w in word_tests if str(num) in load_json(word_answers_path(w["id"]),{})}
    hw_items       = get_hw_items()
    hw_done        = load_json(homework_path(), {}).get(str(num), [])
    notices        = load_json(notices_path(), [])
    study_topics   = get_study_topics()
    open_boards    = [b for b in get_boards() if b.get("open")]
    return render_template("student.html", num=num,
        active_quizzes=quizzes, active_exams=active_exams,
        active_word_tests=active_wt, submitted_exams=submitted_exams,
        submitted_wt=submitted_wt, shared_files=shared_files, today=today_str(),
        notices=notices, hw_items=hw_items, hw_done=hw_done,
        open_boards=open_boards, study_topics=study_topics)

@app.route("/upload", methods=["POST"])
def upload_file():
    num = get_student_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    f = request.files.get("file")
    if not f or not f.filename or not allowed(f.filename):
        return jsonify({"ok":False,"msg":"파일을 확인해주세요"})
    ts = datetime.now().strftime("%H%M%S")
    f.save(os.path.join(UPLOAD_DIR, f"{num}번_{ts}_{secure_filename(f.filename)}"))
    return jsonify({"ok":True,"msg":f"'{f.filename}' 제출 완료!"})

@app.route("/download/<filename>")
def download_shared(filename):
    if not get_student_num() and not is_teacher(): return redirect(url_for("index"))
    return send_from_directory(SHARE_DIR, filename, as_attachment=True)

@app.route("/quiz/<qid>/submit", methods=["POST"])
def quiz_submit(qid):
    num = get_student_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    answers = load_json(quiz_answers_path(qid), {})
    if str(num) in answers: return jsonify({"ok":False,"msg":"이미 제출했어요!"})
    data = request.get_json()
    answers[str(num)] = {"answers":data.get("answers",{}),"submitted_at":datetime.now().strftime("%H:%M:%S")}
    save_json(quiz_answers_path(qid), answers)
    return jsonify({"ok":True,"msg":"제출 완료!"})

@app.route("/exam/<eid>/submit", methods=["POST"])
def exam_submit(eid):
    num = get_student_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    exams = load_json(exams_path(), [])
    exam  = next((e for e in exams if e["id"]==eid), None)
    if not exam: return jsonify({"ok":False,"msg":"시험 없음"})
    all_ans = load_json(exam_answers_path(eid), {})
    if str(num) in all_ans: return jsonify({"ok":False,"msg":"이미 제출했어요!"})
    data = request.get_json()
    student_ans = data.get("answers", {})
    questions   = exam.get("questions", [])
    # 구버전 호환: questions 없으면 answer_key 방식
    if not questions:
        answer_key = exam.get("answer_key", {})
        total_q = exam.get("question_count", 20)
        per_q   = 100/total_q if total_q else 5
        score, results = 0, {}
        for i in range(1, total_q+1):
            k = str(i)
            s = student_ans.get(k,"").strip()
            c = str(answer_key.get(k,"")).strip()
            ok = (s==c) if c else None
            results[k] = {"text":"","student":s,"correct":c,"is_right":ok}
            if ok: score += per_q
        score = round(score)
    else:
        total_q = len(questions)
        per_q   = 100/total_q if total_q else 5
        score, results = 0, {}
        for i, q in enumerate(questions):
            k = str(i+1)
            s = student_ans.get(k,"").strip()
            c = q.get("answer","").strip()
            ok = (s.lower()==c.lower()) if c else None
            results[k] = {"text": q.get("text",""), "student":s, "correct":c, "is_right":ok}
            if ok: score += per_q
        score = round(score)
    all_ans[str(num)] = {"answers":student_ans,"results":results,"score":score,
                         "submitted_at":datetime.now().strftime("%H:%M:%S"),"date":date.today().isoformat()}
    save_json(exam_answers_path(eid), all_ans)
    return jsonify({"ok":True,"msg":f"제출 완료! 점수: {score}점","score":score,"results":results,"questions":questions})

# ══════════════════════════════════════════════════
# 단어시험 - 학생
# ══════════════════════════════════════════════════
@app.route("/word_test/<wid>")
def word_test_page(wid):
    num = get_student_num()
    if not num: return redirect(url_for("index"))
    tests = load_json(word_tests_path(), [])
    test  = next((w for w in tests if w["id"]==wid), None)
    if not test or not test.get("active"): return redirect(url_for("student_dashboard"))
    all_ans = load_json(word_answers_path(wid), {})
    if str(num) in all_ans:
        return render_template("word_test_result.html", num=num,
            test=test, result=all_ans[str(num)])
    # 문제 순서 랜덤 섞기
    words = list(enumerate(test["words"]))  # [(원래idx, word), ...]
    random.seed(num)  # 학생마다 같은 순서 (재접속해도 동일)
    random.shuffle(words)
    return render_template("word_test.html", num=num, test=test, words=words)

@app.route("/word_test/<wid>/submit", methods=["POST"])
def word_test_submit(wid):
    num = get_student_num()
    if not num: return jsonify({"ok":False,"msg":"로그인 필요"})
    tests = load_json(word_tests_path(), [])
    test  = next((w for w in tests if w["id"]==wid), None)
    if not test: return jsonify({"ok":False,"msg":"시험 없음"})
    all_ans = load_json(word_answers_path(wid), {})
    if str(num) in all_ans: return jsonify({"ok":False,"msg":"이미 제출했어요!"})
    data    = request.get_json()
    student = data.get("answers", {})  # {원래인덱스: 학생답}
    direction = test.get("direction", "ko_to_en")
    words = test["words"]
    total = len(words)

    # 화면과 동일하게 random.seed(num)으로 셔플된 순서 재현
    import random as _random
    shuffled = list(enumerate(words))  # [(원래idx, word), ...]
    _random.seed(num)
    _random.shuffle(shuffled)

    score, results = 0, []
    for screen_pos, (orig_i, word) in enumerate(shuffled):
        # 학생 답안은 orig_i 키로 저장됨
        s_ans = student.get(str(orig_i), "").strip()

        # 방향 결정: 화면과 동일하게 screen_pos 기준
        if direction == "ko_to_en":
            correct = word["en"].strip()
            question = word["ko"]
        elif direction == "en_to_ko":
            correct = word["ko"].strip()
            question = word["en"]
        else:  # mixed: 화면 순서(screen_pos) 기준
            if screen_pos % 2 == 0:
                correct = word["en"].strip()
                question = word["ko"]
            else:
                correct = word["ko"].strip()
                question = word["en"]

        is_right = s_ans.lower() == correct.lower()
        if is_right: score += 1
        results.append({"q": question, "correct": correct,
                        "student": s_ans, "is_right": is_right})
    score_pct = round(score / total * 100) if total else 0
    record = {"answers": student, "results": results,
              "score": score, "total": total, "score_pct": score_pct,
              "submitted_at": datetime.now().strftime("%H:%M:%S"),
              "date": date.today().isoformat()}
    all_ans[str(num)] = record
    save_json(word_answers_path(wid), all_ans)
    return jsonify({"ok":True, "score":score, "total":total, "score_pct":score_pct, "results":results})

# ══════════════════════════════════════════════════
# 선생님 대시보드
# ══════════════════════════════════════════════════
@app.route("/teacher")
def teacher_dashboard():
    if not is_teacher(): return redirect(url_for("index"))
    att    = load_json(attendance_path(), {})
    checked = sorted([int(k) for k in att])
    absent  = [n for n in range(1,STUDENT_COUNT+1) if n not in checked]
    quizzes = load_json(quiz_path(), [])
    exams   = load_json(exams_path(), [])
    word_tests = load_json(word_tests_path(), [])
    shared_files = sorted(os.listdir(SHARE_DIR))
    uploads = sorted(os.listdir(UPLOAD_DIR))
    passwords = load_json(passwords_path(), {})
    registered = [int(k) for k in passwords]
    for q in quizzes: q["submit_count"] = len(load_json(quiz_answers_path(q["id"]),{}))
    for e in exams:
        ans = load_json(exam_answers_path(e["id"]),{})
        e["submit_count"] = len(ans)
        scores = [v["score"] for v in ans.values() if "score" in v]
        e["avg_score"] = round(sum(scores)/len(scores)) if scores else "-"
    for w in word_tests:
        ans = load_json(word_answers_path(w["id"]),{})
        w["submit_count"] = len(ans)
        scores = [v["score_pct"] for v in ans.values() if "score_pct" in v]
        w["avg_score"] = round(sum(scores)/len(scores)) if scores else "-"
    notices  = load_json(notices_path(), [])
    study_topics = get_study_topics()
    hw_items = get_hw_items()
    hw_today = load_json(homework_path(), {})
    boards = get_boards()
    return render_template("teacher.html",
        att=att, checked=checked, absent=absent,
        quizzes=quizzes, exams=exams,
        word_tests=word_tests, shared_files=shared_files,
        uploads=uploads, today=today_str(),
        total=STUDENT_COUNT, registered=registered,
        notices=notices, hw_items=hw_items, hw_today=hw_today,
        boards=boards, study_topics=study_topics)

# ── 단어시험 만들기 ─────────────────────────────────
@app.route("/teacher/word_test/add", methods=["POST"])
def word_test_add():
    if not is_teacher(): return redirect(url_for("index"))
    tests = load_json(word_tests_path(), [])
    title = request.form.get("title","").strip()
    direction = request.form.get("direction","ko_to_en")
    words_raw = request.form.get("words","").strip()
    if not title or not words_raw: return redirect(url_for("teacher_dashboard"))
    words = []
    for line in words_raw.split("\n"):
        line = line.strip()
        if not line: continue
        if "," in line:
            parts = [p.strip() for p in line.split(",",1)]
            if len(parts)==2 and parts[0] and parts[1]:
                words.append({"ko": parts[0], "en": parts[1]})
        elif "\t" in line:
            parts = [p.strip() for p in line.split("\t",1)]
            if len(parts)==2:
                words.append({"ko": parts[0], "en": parts[1]})
    if not words: return redirect(url_for("teacher_dashboard"))
    wid = datetime.now().strftime("%Y%m%d%H%M%S")
    tests.append({"id":wid, "title":title, "direction":direction,
                  "words":words, "active":True,
                  "created":datetime.now().strftime("%m/%d %H:%M")})
    save_json(word_tests_path(), tests)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/toggle/<wid>")
def word_test_toggle(wid):
    if not is_teacher(): return redirect(url_for("index"))
    tests = load_json(word_tests_path(), [])
    for w in tests:
        if w["id"]==wid: w["active"] = not w.get("active",True)
    save_json(word_tests_path(), tests)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/delete/<wid>")
def word_test_delete(wid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(word_tests_path(), [w for w in load_json(word_tests_path(),[]) if w["id"]!=wid])
    p = word_answers_path(wid)
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/word_test/<wid>/results")
def word_test_results(wid):
    if not is_teacher(): return redirect(url_for("index"))
    tests = load_json(word_tests_path(), [])
    test  = next((w for w in tests if w["id"]==wid), None)
    if not test: return redirect(url_for("teacher_dashboard"))
    answers = load_json(word_answers_path(wid), {})
    return render_template("word_test_results.html",
        test=test, answers=answers, total=STUDENT_COUNT)


# ── Day 버튼으로 단어시험 즉시 생성 ─────────────────
@app.route("/teacher/word_test/from_day", methods=["POST"])
def word_test_from_day():
    if not is_teacher(): return redirect(url_for("index"))
    day   = int(request.form.get("day", 1))
    direction = request.form.get("direction", "ko_to_en")
    words = WORD_DAYS.get(day, [])
    if not words: return redirect(url_for("teacher_dashboard"))
    tests = load_json(word_tests_path(), [])
    wid   = datetime.now().strftime("%Y%m%d%H%M%S")
    dir_label = {"ko_to_en":"한->영","en_to_ko":"영->한","mixed":"혼합"}.get(direction,"")
    tests.append({"id":wid,
                  "title":f"Day {day} 단어시험 ({dir_label})",
                  "direction":direction,
                  "words":words, "active":True,
                  "created":datetime.now().strftime("%m/%d %H:%M"),
                  "day": day})
    save_json(word_tests_path(), tests)
    return redirect(url_for("teacher_dashboard"))

# ── 나머지 선생님 라우트 ────────────────────────────
@app.route("/teacher/student/<int:num>")
def student_detail(num):
    if not is_teacher(): return redirect(url_for("index"))
    att_dates = get_all_attendance_dates()
    att_records = {d: {"present": str(num) in load_json(attendance_path(d),{}),
                       "time": load_json(attendance_path(d),{}).get(str(num),"")} for d in att_dates}
    uploads = [f for f in sorted(os.listdir(UPLOAD_DIR)) if f.startswith(f"{num}번_")]
    quizzes = load_json(quiz_path(), [])
    quiz_records = [{"title":q["title"],"data":load_json(quiz_answers_path(q["id"]),{}).get(str(num)),"questions":q["questions"]}
                    for q in quizzes if str(num) in load_json(quiz_answers_path(q["id"]),{})]
    exams = load_json(exams_path(), [])
    exam_records = [{"title":e["title"],"data":load_json(exam_answers_path(e["id"]),{}).get(str(num))}
                    for e in exams if str(num) in load_json(exam_answers_path(e["id"]),{})]
    word_tests = load_json(word_tests_path(), [])
    wt_records = [{"title":w["title"],"data":load_json(word_answers_path(w["id"]),{}).get(str(num))}
                  for w in word_tests if str(num) in load_json(word_answers_path(w["id"]),{})]
    present_count = sum(1 for v in att_records.values() if v["present"])
    return render_template("student_detail.html", num=num,
        att_records=att_records, present_count=present_count,
        total_days=len(att_dates), uploads=uploads,
        quiz_records=quiz_records, exam_records=exam_records,
        wt_records=wt_records)



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
    p = os.path.join(SHARE_DIR, secure_filename(filename))
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/uploads/<filename>")
def teacher_download_upload(filename):
    if not is_teacher(): return redirect(url_for("index"))
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route("/teacher/uploads/delete/<filename>")
def teacher_delete_upload(filename):
    if not is_teacher(): return redirect(url_for("index"))
    p = os.path.join(UPLOAD_DIR, secure_filename(filename))
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/attendance/export")
def export_attendance():
    if not is_teacher(): return redirect(url_for("index"))
    att = load_json(attendance_path(), {})
    from io import StringIO
    si = StringIO(); w = csv.writer(si)
    w.writerow(["번호","출석","시각"])
    for n in range(1,STUDENT_COUNT+1):
        k=str(n); w.writerow([f"{n}번","출석" if k in att else "결석",att.get(k,"")])
    return Response("\ufeff"+si.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition":f"attachment;filename=출석_{date.today()}.csv"})

@app.route("/teacher/quiz/add", methods=["POST"])
def quiz_add():
    if not is_teacher(): return redirect(url_for("index"))
    quizzes = load_json(quiz_path(), [])
    title = request.form.get("title","").strip()
    if not title: return redirect(url_for("teacher_dashboard"))
    qs = []
    # qq_text_N 키를 모두 수집해서 번호 순으로 정렬 처리 (삭제 후 재추가 시 번호 불연속 대응)
    import re as _re
    text_keys = sorted(
        [k for k in request.form.keys() if _re.match(r"qq_text_\d+$", k)],
        key=lambda k: int(_re.search(r"\d+$", k).group())
    )
    for key in text_keys:
        q_text = request.form.get(key, "").strip()
        if not q_text: continue
        n = _re.search(r"\d+$", key).group()
        q_type   = request.form.get(f"qq_type_{n}", "short")
        q_answer = request.form.get(f"qq_answer_{n}", "").strip()
        choices = []
        for j in range(1, 6):
            c = request.form.get(f"qq_choice_{n}_{j}", "").strip()
            if c: choices.append(c)
        q = {"text": q_text, "type": q_type, "answer": q_answer}
        if q_type == "choice" and choices:
            q["choices"] = choices
        elif q_type == "ox":
            q["choices"] = ["O", "X"]
            q["answer"] = ""
        qs.append(q)
    if qs:
        qid = datetime.now().strftime("%Y%m%d%H%M%S")
        quizzes.append({"id":qid,"title":title,"questions":qs,
                        "active":True,"created":datetime.now().strftime("%m/%d %H:%M")})
        save_json(quiz_path(), quizzes)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/toggle/<qid>")
def quiz_toggle(qid):
    if not is_teacher(): return redirect(url_for("index"))
    qs = load_json(quiz_path(),[])
    for q in qs:
        if q["id"]==qid: q["active"] = not q.get("active",True)
    save_json(quiz_path(), qs)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/delete/<qid>")
def quiz_delete(qid):
    if not is_teacher(): return redirect(url_for("index"))
    save_json(quiz_path(),[q for q in load_json(quiz_path(),[]) if q["id"]!=qid])
    p=quiz_answers_path(qid)
    if os.path.exists(p): os.remove(p)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/quiz/<qid>/results")
def quiz_results(qid):
    if not is_teacher(): return redirect(url_for("index"))
    quiz = next((q for q in load_json(quiz_path(),[]) if q["id"]==qid),None)
    if not quiz: return redirect(url_for("teacher_dashboard"))
    answers = load_json(quiz_answers_path(qid),{})
    not_submitted = [n for n in range(1,STUDENT_COUNT+1) if str(n) not in answers]
    return render_template("quiz_results.html", quiz=quiz,
        answers=answers, total=STUDENT_COUNT, not_submitted=not_submitted)

@app.route("/teacher/exam/add", methods=["POST"])
def exam_add():
    if not is_teacher(): return redirect(url_for("index"))
    exams = load_json(exams_path(),[])
    title = request.form.get("title","").strip()
    if not title: return redirect(url_for("teacher_dashboard"))
    # 문제/정답 파싱: q_text_1, q_ans_1, q_text_2, q_ans_2 ...
    # OMR 방식: 문항수 + 정답만 입력
    import re as _re
    q_count = int(request.form.get("question_count", 20))
    answer_key = {}
    for i in range(1, q_count + 1):
        ans = request.form.get(f"ans_{i}", "").strip()
        if ans:
            answer_key[str(i)] = ans
    questions = [{"text": f"{i}번", "answer": answer_key.get(str(i), "")} for i in range(1, q_count + 1)]
    if not questions: return redirect(url_for("teacher_dashboard"))
    eid = datetime.now().strftime("%Y%m%d%H%M%S")
    exams.append({"id":eid, "title":title,
                  "question_count": len(questions),
                  "questions": questions,
                  "active":True,
                  "created":datetime.now().strftime("%m/%d %H:%M")})
    save_json(exams_path(), exams)
    return redirect(url_for("teacher_dashboard"))

@app.route("/teacher/exam/toggle/<eid>")
def exam_toggle(eid):
    if not is_teacher(): return redirect(url_for("index"))
    es=load_json(exams_path(),[])
    for e in es:
        if e["id"]==eid: e["active"]=not e.get("active",True)
    save_json(exams_path(),es)
    return redirect(url_for("teacher_dashboard"))

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
    return render_template("exam_results.html", exam=exam,
        answers=load_json(exam_answers_path(eid),{}), total=STUDENT_COUNT)

@app.route("/teacher/reset_pw/<int:num>")
def reset_student_pw(num):
    if not is_teacher(): return redirect(url_for("index"))
    pw=load_json(passwords_path(),{}); pw.pop(str(num),None)
    save_json(passwords_path(),pw)
    return redirect(url_for("teacher_dashboard"))


@app.route("/wordbook")
def wordbook():
    num = get_student_num()
    if not num: return redirect(url_for("index"))
    return render_template("wordbook.html", num=num, word_days=WORD_DAYS)



# ── 공지사항 ───────────────────────────────────────────
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
    save_json(notices_path(), [n for n in load_json(notices_path(),[]) if n["id"]!=nid])
    return redirect(url_for("teacher_dashboard"))

# ── 숙제 체크 ──────────────────────────────────────
@app.route("/homework/check", methods=["POST"])
def homework_check():
    num = get_student_num()
    if not num: return jsonify({"ok": False, "msg": "로그인 필요"})
    data = request.get_json()
    item_id = data.get("item_id", "")
    checked = data.get("checked", False)
    hw = load_json(homework_path(), {})
    key = str(num)
    if key not in hw: hw[key] = []
    if checked and item_id not in hw[key]:
        hw[key].append(item_id)
    elif not checked and item_id in hw[key]:
        hw[key].remove(item_id)
    save_json(homework_path(), hw)
    return jsonify({"ok": True})

# ── 숙제 항목 관리 (선생님) ────────────────────────
@app.route("/teacher/homework/save", methods=["POST"])
def homework_save():
    if not is_teacher(): return redirect(url_for("index"))
    data = request.get_json()
    items = data.get("items", [])
    # 기존 id 유지하면서 이름만 업데이트
    current = get_hw_items()
    for i, item in enumerate(current):
        if i < len(items) and items[i].get("name","").strip():
            item["name"] = items[i]["name"].strip()
    save_json(homework_items_path(), current)
    return jsonify({"ok": True, "items": current})

@app.route("/teacher/homework/reset", methods=["POST"])
def homework_reset():
    """오늘 숙제 체크 초기화"""
    if not is_teacher(): return redirect(url_for("index"))
    import os as _os
    p = homework_path()
    if _os.path.exists(p): _os.remove(p)
    return jsonify({"ok": True})


# ── 다중 게시판 ───────────────────────────────────────
@app.route("/boards")
def boards_list():
    num = get_student_num()
    if not num and not is_teacher(): return redirect(url_for("index"))
    boards = get_boards()
    # 학생은 열린 게시판만
    if not is_teacher():
        boards = [b for b in boards if b.get("open")]
    return render_template("boards.html", boards=boards, is_teacher=is_teacher(), num=num)

@app.route("/board/<bid>")
def board(bid):
    num = get_student_num()
    if not num and not is_teacher(): return redirect(url_for("index"))
    b = get_board(bid)
    if not b: return redirect(url_for("boards_list"))
    if not is_teacher() and not b.get("open"): return redirect(url_for("student_dashboard"))
    posts = load_json(board_posts_path(bid), [])
    return render_template("board.html", posts=posts, num=num,
        is_teacher=is_teacher(), board=b)

@app.route("/board/<bid>/post", methods=["POST"])
def board_post(bid):
    num = get_student_num()
    if not num: return jsonify({"ok": False, "msg": "로그인 필요"})
    b = get_board(bid)
    if not b or not b.get("open"): return jsonify({"ok": False, "msg": "닫힌 게시판이에요"})
    content = request.form.get("content", "").strip()
    image_url = ""
    if "image" in request.files:
        f = request.files["image"]
        if f and f.filename:
            ext = f.filename.rsplit(".",1)[-1].lower()
            if ext in {"jpg","jpeg","png","gif","webp"}:
                ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
                fname = f"{num}번_{ts}.{ext}"
                f.save(os.path.join(BOARD_UPLOAD_DIR, fname))
                image_url = f"/board_image/{fname}"
    if not content and not image_url:
        return jsonify({"ok": False, "msg": "내용이나 사진을 추가해주세요"})
    posts = load_json(board_posts_path(bid), [])
    posts.insert(0, {"id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "num": num, "content": content, "image_url": image_url,
        "created": datetime.now().strftime("%m/%d %H:%M")})
    save_json(board_posts_path(bid), posts)
    return jsonify({"ok": True})

@app.route("/board/<bid>/delete/<pid>")
def board_delete(bid, pid):
    if not get_student_num() and not is_teacher(): return redirect(url_for("index"))
    num = get_student_num()
    posts = load_json(board_posts_path(bid), [])
    new_posts = []
    for p in posts:
        if p["id"] == pid:
            if is_teacher() or p["num"] == num:
                if p.get("image_url"):
                    fname = p["image_url"].split("/")[-1]
                    fpath = os.path.join(BOARD_UPLOAD_DIR, fname)
                    if os.path.exists(fpath): os.remove(fpath)
                continue
        new_posts.append(p)
    save_json(board_posts_path(bid), new_posts)
    return jsonify({"ok": True})

@app.route("/board_image/<filename>")
def board_image(filename):
    return send_from_directory(BOARD_UPLOAD_DIR, filename)

# ── 게시판 관리 (선생님) ───────────────────────────────
@app.route("/teacher/board/add", methods=["POST"])
def board_add():
    if not is_teacher(): return jsonify({"ok": False})
    data = request.get_json()
    title = data.get("title","").strip()
    if not title: return jsonify({"ok": False, "msg": "제목을 입력해주세요"})
    boards = get_boards()
    bid = datetime.now().strftime("%Y%m%d%H%M%S%f")
    boards.append({"id": bid, "title": title, "open": True,
                   "created": datetime.now().strftime("%m/%d")})
    set_boards(boards)
    return jsonify({"ok": True, "board": boards[-1]})

@app.route("/teacher/board/toggle/<bid>", methods=["POST"])
def board_toggle(bid):
    if not is_teacher(): return jsonify({"ok": False})
    boards = get_boards()
    for b in boards:
        if b["id"] == bid:
            b["open"] = not b.get("open", True)
            set_boards(boards)
            return jsonify({"ok": True, "open": b["open"]})
    return jsonify({"ok": False})

@app.route("/teacher/board/delete/<bid>", methods=["POST"])
def board_delete_board(bid):
    if not is_teacher(): return jsonify({"ok": False})
    boards = [b for b in get_boards() if b["id"] != bid]
    set_boards(boards)
    p = board_posts_path(bid)
    if os.path.exists(p): os.remove(p)
    return jsonify({"ok": True})


@app.route("/teacher/study/toggle", methods=["POST"])
def study_toggle():
    if not is_teacher(): return jsonify({"ok": False})
    data = request.get_json()
    topic = data.get("topic")
    if topic not in STUDY_TOPICS_DATA: return jsonify({"ok": False})
    topics = get_study_topics()
    topics[topic] = not topics.get(topic, False)
    set_study_topics(topics)
    return jsonify({"ok": True, "active": topics[topic]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
