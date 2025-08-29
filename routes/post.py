from flask import Blueprint, request, session, jsonify
from utils.database_util import DatabaseManager

post_bp = Blueprint('post', __name__)


def _require_login():
    sid = session.get('session_student_id')
    if not sid:
        return None, (jsonify({
            "status": "error",
            "message": "로그인이 필요합니다."
        }), 401)
    # 세션 유효성 (옵션) 확인
    db = DatabaseManager()
    exists = db.query(
        """
        SELECT 1 FROM Students WHERE student_id = %(sid)s
        """,
        sid=sid
    ).result
    if not exists:
        return None, (jsonify({
            "status": "error",
            "message": "유효하지 않은 세션입니다. 다시 로그인해 주세요."
        }), 401)
    return sid, None


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        return v in ("1", "true", "t", "yes", "y", "on")
    return default


@post_bp.route('/posts', methods=['POST'])
def create_post():
    try:
        sid, err = _require_login()
        if err:
            return err

        payload = request.get_json(silent=True) or {}
        title = (payload.get('title') or '').strip()
        content = (payload.get('content') or '').strip()
        is_anonymous = 1 if _to_bool(payload.get('is_anonymous'), False) else 0

        if not title or not content:
            return jsonify({
                "status": "error",
                "message": "제목과 내용을 모두 입력하세요."
            }), 400

        db = DatabaseManager()
        db.query(
            """
            INSERT INTO Posts (student_id, title, content, is_anonymous)
            VALUES (%(sid)s, %(title)s, %(content)s, %(is_anonymous)s)
            """,
            sid=sid,
            title=title,
            content=content,
            is_anonymous=is_anonymous
        )
        post_id_row = db.query("SELECT LAST_INSERT_ID()")
        db.commit()

        # LAST_INSERT_ID() 결과 파싱
        post_id = None
        if post_id_row.result and len(post_id_row.result[0]) > 0:
            post_id = post_id_row.result[0][0]

        return jsonify({
            "status": "success",
            "message": "게시물 작성 성공",
            "post_id": post_id
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "서버 오류가 발생했습니다.",
            "detail": str(e)
        }), 500


@post_bp.route('/posts', methods=['GET'])
def list_posts():
    try:
        # 페이징 파라미터
        try:
            page = int(request.args.get('page', 1))
            size = int(request.args.get('size', 10))
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "유효한 페이지/크기를 입력하세요."
            }), 400

        if page < 1 or size < 1 or size > 100:
            return jsonify({
                "status": "error",
                "message": "페이지는 1 이상, 크기는 1~100 사이여야 합니다."
            }), 400

        offset = (page - 1) * size

        db = DatabaseManager()
        total = db.query("SELECT COUNT(*) FROM Posts").result[0][0]

        rows = db.query(
            """
            SELECT 
                p.post_id,
                p.student_id,
                s.student_name,
                p.title,
                p.content,
                p.is_anonymous,
                p.like_count,
                DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at,
                (SELECT COUNT(*) FROM Comments c WHERE c.post_id = p.post_id) as comment_count
            FROM Posts p
            LEFT JOIN Students s ON p.student_id = s.student_id
            ORDER BY p.post_id DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            limit=size,
            offset=offset
        ).result

        items = []
        for r in rows:
            (post_id, student_id, student_name, title, content, is_anonymous,
             like_count, created_at, comment_count) = r
            anon = bool(is_anonymous)
            items.append({
                "post_id": post_id,
                "student_id": None if anon else student_id,
                "student_name": "익명" if anon else student_name,
                "title": title,
                "content": content,
                "is_anonymous": anon,
                "like_count": like_count,
                "comment_count": comment_count,
                "created_at": created_at
            })

        return jsonify({
            "status": "success",
            "page": page,
            "size": size,
            "total": total,
            "items": items
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "서버 오류가 발생했습니다.",
            "detail": str(e)
        }), 500


@post_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id: int):
    try:
        db = DatabaseManager()
        post_row = db.query(
            """
            SELECT 
                p.post_id,
                p.student_id,
                s.student_name,
                p.title,
                p.content,
                p.is_anonymous,
                p.like_count,
                DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at
            FROM Posts p
            LEFT JOIN Students s ON p.student_id = s.student_id
            WHERE p.post_id = %(post_id)s
            """,
            post_id=post_id
        ).result

        if not post_row:
            return jsonify({
                "status": "error",
                "message": "게시물을 찾을 수 없습니다."
            }), 404

        (pid, student_id, student_name, title, content, is_anonymous,
         like_count, created_at) = post_row[0]
        anon = bool(is_anonymous)
        post_obj = {
            "post_id": pid,
            "student_id": None if anon else student_id,
            "student_name": "익명" if anon else student_name,
            "title": title,
            "content": content,
            "is_anonymous": anon,
            "like_count": like_count,
            "created_at": created_at
        }

        comments = db.query(
            """
            SELECT 
                c.comment_id,
                c.student_id,
                s.student_name,
                c.content,
                c.is_anonymous,
                DATE_FORMAT(c.created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at
            FROM Comments c
            LEFT JOIN Students s ON c.student_id = s.student_id
            WHERE c.post_id = %(post_id)s
            ORDER BY c.created_at ASC
            """,
            post_id=post_id
        ).result

        comment_items = []
        for r in comments:
            (cid, c_student_id, c_student_name, c_content, c_is_anonymous, c_created_at) = r
            c_anon = bool(c_is_anonymous)
            comment_items.append({
                "comment_id": cid,
                "student_id": None if c_anon else c_student_id,
                "student_name": "익명" if c_anon else c_student_name,
                "content": c_content,
                "is_anonymous": c_anon,
                "created_at": c_created_at
            })

        return jsonify({
            "status": "success",
            "post": post_obj,
            "comments": comment_items
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "서버 오류가 발생했습니다.",
            "detail": str(e)
        }), 500


@post_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id: int):
    try:
        sid, err = _require_login()
        if err:
            return err

        payload = request.get_json(silent=True) or {}
        content = (payload.get('content') or '').strip()
        is_anonymous = 1 if _to_bool(payload.get('is_anonymous'), False) else 0

        if not content:
            return jsonify({
                "status": "error",
                "message": "댓글 내용을 입력하세요."
            }), 400

        db = DatabaseManager()

        # 게시물 존재 여부 확인
        exists = db.query(
            "SELECT 1 FROM Posts WHERE post_id = %(post_id)s",
            post_id=post_id
        ).result
        if not exists:
            return jsonify({
                "status": "error",
                "message": "게시물을 찾을 수 없습니다."
            }), 404

        db.query(
            """
            INSERT INTO Comments (post_id, student_id, content, is_anonymous)
            VALUES (%(post_id)s, %(sid)s, %(content)s, %(is_anonymous)s)
            """,
            post_id=post_id,
            sid=sid,
            content=content,
            is_anonymous=is_anonymous
        )
        cid_row = db.query("SELECT LAST_INSERT_ID()")
        db.commit()

        comment_id = None
        if cid_row.result and len(cid_row.result[0]) > 0:
            comment_id = cid_row.result[0][0]

        return jsonify({
            "status": "success",
            "message": "댓글 작성 성공",
            "comment_id": comment_id
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "서버 오류가 발생했습니다.",
            "detail": str(e)
        }), 500


@post_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id: int):
    try:
        sid, err = _require_login()
        if err:
            return err

        db = DatabaseManager()
        # 게시물 존재 확인
        post_exists = db.query(
            "SELECT 1 FROM Posts WHERE post_id = %(post_id)s",
            post_id=post_id
        ).result
        if not post_exists:
            return jsonify({
                "status": "error",
                "message": "게시물을 찾을 수 없습니다."
            }), 404

        liked_row = db.query(
            """
            SELECT 1 FROM PostLikes 
            WHERE post_id = %(post_id)s AND student_id = %(sid)s
            """,
            post_id=post_id,
            sid=sid
        ).result

        if liked_row:
            # 좋아요 취소
            db.query(
                "DELETE FROM PostLikes WHERE post_id = %(post_id)s AND student_id = %(sid)s",
                post_id=post_id,
                sid=sid
            )
            db.query(
                "UPDATE Posts SET like_count = GREATEST(like_count - 1, 0) WHERE post_id = %(post_id)s",
                post_id=post_id
            )
            liked = False
        else:
            # 좋아요 추가
            db.query(
                "INSERT INTO PostLikes (post_id, student_id) VALUES (%(post_id)s, %(sid)s)",
                post_id=post_id,
                sid=sid
            )
            db.query(
                "UPDATE Posts SET like_count = like_count + 1 WHERE post_id = %(post_id)s",
                post_id=post_id
            )
            liked = True

        count_row = db.query(
            "SELECT like_count FROM Posts WHERE post_id = %(post_id)s",
            post_id=post_id
        ).result
        db.commit()

        like_count = count_row[0][0] if count_row else 0

        return jsonify({
            "status": "success",
            "liked": liked,
            "like_count": like_count
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "서버 오류가 발생했습니다.",
            "detail": str(e)
        }), 500
