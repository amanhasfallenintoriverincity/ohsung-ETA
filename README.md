<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=150&section=header&text=오성에타&fontSize=40&fontColor=ffffff" />

# 오성에타

> 천안오성고 19대 학생회 **AI부**에서 제작한,  
> 학교 전용 통합 서비스 플랫폼입니다.  
> 실제 서비스로 운영되며 학생들이 더 편리하게 학교생활을 누릴 수 있도록 개발 중입니다.

---

## Tech Stack

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) 
![HTML](https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white) 
![CSS](https://img.shields.io/badge/CSS-239120?style=for-the-badge&logo=css3&logoColor=white) 
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=black) 

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) 
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

### Environment
- Flask + MySQL 기반
- CORS & Session 지원
- Node.js 기반 React 프론트엔드

---

## Project Structure

```
everytime/
 ├── app.py                # Flask 실행
 ├── config.json           # 환경 설정
 ├── requirements.txt      # Python 의존성
 ├── routes/               # 주요 API 라우트
 │    ├── auth.py          # 로그인
 │    ├── main_page.py     # 메인 페이지 데이터
 │    ├── meal.py          # 급식표
 │    ├── post.py          # 게시물
 │    ├── profile.py       # 프로필 관리
 │    ├── schedule.py      # 학사일정
 │    └── timetable.py     # 시간표
 ├── utils/                # 유틸리티
 │    ├── config_util.py
 │    ├── database_util.py
 │    ├── json_util.py
 │    └── student_util.py
 └── flask_session/        # 세션 데이터 저장
```

---

## Features

<details>
<summary><b>로그인 / 인증</b></summary>

- 학생 계정 로그인  
- 세션 기반 인증  
- 사용자 권한 관리  
</details>

<details>
<summary><b>메인 페이지</b></summary>

- 요약 정보 제공  
- 주요 기능 바로가기  
</details>

<details>
<summary><b>급식표</b></summary>

- 날짜별 급식 조회 API  
</details>

<details>
<summary><b>게시물</b></summary>

- 게시물 CRUD 기
- 사용자별 게시물 관리  
</details>

<details>
<summary><b>프로필</b></summary>

- 사용자 프로필 조회 / 수정  
</details>

<details>
<summary><b>학사일정</b></summary>

- 학사 일정표 제공  
</details>

<details>
<summary><b>시간표</b></summary>

- 학년/반 기준 시간표 제공  
</details>

---

## Installation & Run

### Backend (Flask)
```bash
cd everytime
pip install -r requirements.txt
flask run
```

### Frontend (React)
```bash
npm install
npm run dev
```

---

## Contributors
- **천안오성고 19대 학생회 AI부**

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=150&section=footer" />
