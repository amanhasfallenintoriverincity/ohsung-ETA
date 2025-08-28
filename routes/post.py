from flask import Blueprint, request, session, jsonify
from utils.database_util import DatabaseManager
import pymysql

post_bp = Blueprint('post', __name__)

def _require_login():
    student_id = session.get('session_student_id')
    if not student_id:
        return None, (jsonify({"status": "error", "message": "로그인이 필요합니다."}), 401)
    return student_id, None

def _to_bool_flag(value) -> int:
    return 1 if value in (True, 1, "1", "true", "True") else 0

@post_bp.route("/posts", methods=["POST"])
def create_post():
    try:
        student_id, error = _require_login()
        if error:
            return error

        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        content = (data.get("content") or "").strip()
        is_anonymous = _to_bool_flag(data.get("is_anonymous", False))

        if not title or not content:
            return jsonify({"status": "error", "message": "제목과 내용을 모두 입력하세요."}), 400

        db = DatabaseManager()

        # 세션 학생 존재 확인 (FK 오류 예방)
        exists = db.query(
            "SELECT 1 FROM Students WHERE student_id = %(student_id)s",
            student_id=student_id
        ).result
        if not exists:
            return jsonify({"status": "error", "message": "유효하지 않은 세션입니다. 다시 로그인해 주세요."}), 401

        db.query(
            """
            INSERT INTO Posts (student_id, title, content, is_anonymous)
            VALUES (%(student_id)s, %(title)s, %(content)s, %(is_anonymous)s)
            """,
            student_id=student_id,
            title=title,
            content=content,
            is_anonymous=is_anonymous
        )
        post_id_row = db.query("SELECT LAST_INSERT_ID()").result
        db.commit()

        post_id = post_id_row[0][0] if post_id_row else None

        return jsonify({
            "status": "success",
            "message": "게시물 작성 성공",
            "post_id": post_id
        }), 201

    except pymysql.err.IntegrityError as e:
        return jsonify({"status": "error", "message": "데이터 무결성 오류", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "서버 오류", "detail": str(e)}), 500

@post_bp.route("/posts", methods=["GET"])
def list_posts():
    try:
        db = DatabaseManager()

        # 페이지네이션 파라미터
        try:
            page = int(request.args.get("page", 1))
            size = int(request.args.get("size", 10))
        except ValueError:
            return jsonify({"status": "error", "message": "잘못된 페이지 파라미터입니다."}), 400

        page = 1 if page < 1 else page
        size = 1 if size < 1 else (100 if size > 100 else size)
        offset = (page - 1) * size

        total_row = db.query("SELECT COUNT(*) FROM Posts").result
        total = total_row[0][0] if total_row else 0

        rows = db.query(
            """
            SELECT
                p.post_id,
                CASE WHEN p.is_anonymous = 1 THEN NULL ELSE p.student_id END AS student_id,
                CASE WHEN p.is_anonymous = 1 THEN '익명' ELSE s.student_name END AS student_name,
                p.title,
                p.content,
                p.is_anonymous,
                p.like_count,
                p.created_at,
                (SELECT COUNT(*) FROM Comments c WHERE c.post_id = p.post_id) AS comment_count
            FROM Posts p
            LEFT JOIN Students s ON s.student_id = p.student_id
            ORDER BY p.created_at DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            limit=size,
            offset=offset
        ).result

        items = []
        for r in rows:
            (
                post_id,
                student_id,
                student_name,
                title,
                content,
                is_anonymous,
                like_count,
                created_at,
                comment_count
            ) = r
            items.append({
                "post_id": post_id,
                "student_id": student_id,
                "student_name": student_name,
                "title": title,
                "content": content,
                "is_anonymous": bool(is_anonymous),
                "like_count": like_count,
                "comment_count": comment_count,
                "created_at": str(created_at)
            })

        return jsonify({
            "status": "success",
            "page": page,
            "size": size,
            "total": total,
            "items": items
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "서버 오류", "detail": str(e)}), 500

@post_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
def create_comment(post_id: int):
    try:
        student_id, error = _require_login()
        if error:
            return error

        data = request.get_json(silent=True) or {}
        content = (data.get("content") or "").strip()
        is_anonymous = _to_bool_flag(data.get("is_anonymous", False))

        if not content:
            return jsonify({"status": "error", "message": "댓글 내용을 입력하세요."}), 400

        db = DatabaseManager()

        # 대상 게시물 존재 확인
        exists = db.query(
            "SELECT 1 FROM Posts WHERE post_id = %(post_id)s",
            post_id=post_id
        ).result
        if not exists:
            return jsonify({"status": "error", "message": "존재하지 않는 게시물입니다."}), 404

        db.query(
            """
            INSERT INTO Comments (post_id, student_id, content, is_anonymous)
            VALUES (%(post_id)s, %(student_id)s, %(content)s, %(is_anonymous)s)
            """,
            post_id=post_id,
            student_id=student_id,
            content=content,
            is_anonymous=is_anonymous
        )
        comment_id_row = db.query("SELECT LAST_INSERT_ID()").result
        db.commit()

        comment_id = comment_id_row[0][0] if comment_id_row else None

        return jsonify({
            "status": "success",
            "message": "댓글 작성 성공",
            "comment_id": comment_id
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": "서버 오류", "detail": str(e)}), 500

@post_bp.route("/posts/<int:post_id>/like", methods=["POST"])
def toggle_like(post_id: int):
    try:
        student_id, error = _require_login()
        if error:
            return error

        db = DatabaseManager()

        # 게시물 존재 확인
        post_exists = db.query(
            "SELECT 1 FROM Posts WHERE post_id = %(post_id)s",
            post_id=post_id
        ).result
        if not post_exists:
            return jsonify({"status": "error", "message": "존재하지 않는 게시물입니다."}), 404

        liked_row = db.query(
            """
            SELECT 1 FROM PostLikes
            WHERE post_id = %(post_id)s AND student_id = %(student_id)s
            """,
            post_id=post_id,
            student_id=student_id
        ).result

        if liked_row:
            # 좋아요 취소
            db.query(
                """
                DELETE FROM PostLikes
                WHERE post_id = %(post_id)s AND student_id = %(student_id)s
                """,
                post_id=post_id,
                student_id=student_id
            )
            db.query(
                """
                UPDATE Posts
                SET like_count = GREATEST(like_count - 1, 0)
                WHERE post_id = %(post_id)s
                """,
                post_id=post_id
            )
            liked = False
        else:
            # 좋아요 추가
            db.query(
                """
                INSERT INTO PostLikes (post_id, student_id)
                VALUES (%(post_id)s, %(student_id)s)
                """,
                post_id=post_id,
                student_id=student_id
            )
            db.query(
                """
                UPDATE Posts
                SET like_count = like_count + 1
                WHERE post_id = %(post_id)s
                """,
                post_id=post_id
            )
            liked = True

        like_count_row = db.query(
            "SELECT like_count FROM Posts WHERE post_id = %(post_id)s",
            post_id=post_id
        ).result
        db.commit()

        like_count = like_count_row[0][0] if like_count_row else 0

        return jsonify({
            "status": "success",
            "liked": liked,
            "like_count": like_count
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "서버 오류", "detail": str(e)}), 500

@post_bp.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id: int):
    """
    게시물 상세와 해당 게시물의 댓글 목록을 반환합니다.
    """
    try:
        db = DatabaseManager()

        post_row = db.query(
            """
            SELECT
                p.post_id,
                CASE WHEN p.is_anonymous = 1 THEN NULL ELSE p.student_id END AS student_id,
                CASE WHEN p.is_anonymous = 1 THEN '익명' ELSE s.student_name END AS student_name,
                p.title,
                p.content,
                p.is_anonymous,
                p.like_count,
                p.created_at
            FROM Posts p
            LEFT JOIN Students s ON s.student_id = p.student_id
            WHERE p.post_id = %(post_id)s
            """,
            post_id=post_id
        ).result

        if not post_row:
            return jsonify({"status": "error", "message": "존재하지 않는 게시물입니다."}), 404

        pr = post_row[0]
        post = {
            "post_id": pr[0],
            "student_id": pr[1],
            "student_name": pr[2],
            "title": pr[3],
            "content": pr[4],
            "is_anonymous": bool(pr[5]),
            "like_count": pr[6],
            "created_at": str(pr[7])
        }

        # 댓글 조회
        comment_rows = db.query(
            """
            SELECT
                c.comment_id,
                CASE WHEN c.is_anonymous = 1 THEN NULL ELSE c.student_id END AS student_id,
                CASE WHEN c.is_anonymous = 1 THEN '익명' ELSE s.student_name END AS student_name,
                c.content,
                c.is_anonymous,
                c.created_at
            FROM Comments c
            LEFT JOIN Students s ON s.student_id = c.student_id
            WHERE c.post_id = %(post_id)s
            ORDER BY c.created_at ASC
            """,
            post_id=post_id
        ).result

        comments = []
        for cr in comment_rows:
            comments.append({
                "comment_id": cr[0],
                "student_id": cr[1],
                "student_name": cr[2],
                "content": cr[3],
                "is_anonymous": bool(cr[4]),
                "created_at": str(cr[5])
            })

        return jsonify({
            "status": "success",
            "post": post,
            "comments": comments
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "서버 오류", "detail": str(e)}), 500
