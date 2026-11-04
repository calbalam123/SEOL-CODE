# Korin에서 NexaDB .db 파일 연결
db = 데이터베이스("../NexaDB/학교.db")
출력(db.조회("SELECT * FROM 학생"))
db.실행("INSERT INTO 학생 VALUES (?, ?, ?)", ("하늘", 18, "고등학교 2학년"))
출력(db.조회("SELECT * FROM 학생"))
db.닫기()
