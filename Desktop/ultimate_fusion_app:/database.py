# database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# .env ファイルの読み込み
load_dotenv()

# 環境変数からデータベースURLを取得
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ultimate_fusion_app.db")

# SQLAlchemy エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# セッションローカルの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# デクラレーティブベースの作成
Base = declarative_base()

# --------------------------
# モデルの定義
# --------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=False)  # ハッシュ化されたパスワード
    is_admin = Column(Boolean, default=False)

    # リレーションシップ
    feedbacks = relationship("Feedback", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    image_classifications = relationship("ImageClassification", back_populates="user")
    settings = relationship("UserSetting", back_populates="user", uselist=False)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    user = relationship("User", back_populates="feedbacks")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    user = relationship("User", back_populates="activity_logs")


class ImageClassification(Base):
    __tablename__ = "image_classifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String(255), nullable=False)
    classification_result = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    user = relationship("User", back_populates="image_classifications")


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    notify_tts = Column(Boolean, default=True)
    notify_classification = Column(Boolean, default=True)
    notify_feedback = Column(Boolean, default=True)

    # リレーションシップ
    user = relationship("User", back_populates="settings")


# --------------------------
# データベースの初期化
# --------------------------

def init_db():
    """データベースのテーブルを作成します。"""
    Base.metadata.create_all(bind=engine)


# --------------------------
# データベースセッションの取得
# --------------------------

def get_db():
    """データベースセッションを取得します。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------
# ユーザー管理関数
# --------------------------

def hash_password(plain_password: str) -> str:
    """パスワードをハッシュ化します。"""
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証します。"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def user_exists(username: str, db):
    """ユーザーの存在を確認します。"""
    return db.query(User).filter(User.username == username).first() is not None


def email_exists(email: str, db):
    """メールアドレスの存在を確認します。"""
    return db.query(User).filter(User.email == email).first() is not None


def add_user(username: str, name: str, password: str, email: str, db, is_admin: bool = False):
    """新しいユーザーを追加します。"""
    hashed_pw = hash_password(password)
    new_user = User(
        username=username,
        name=name,
        email=email,
        password=hashed_pw,
        is_admin=is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # 初期設定の追加
    add_user_setting(new_user.id, db)
    return new_user


def get_user(username: str, db):
    """ユーザーを取得します。"""
    return db.query(User).filter(User.username == username).first()


def authenticate_user(username: str, password: str, db) -> bool:
    """ユーザーの認証を行います。"""
    user = get_user(username, db)
    if not user:
        return False
    return verify_password(password, user.password)


# --------------------------
# フィードバック管理関数
# --------------------------

def add_feedback(user_id: int, feedback: str, db):
    """フィードバックを追加します。"""
    new_feedback = Feedback(
        user_id=user_id,
        feedback=feedback
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


def get_all_feedback(db):
    """すべてのフィードバックを取得します。"""
    return db.query(Feedback).order_by(Feedback.timestamp.desc()).all()


# --------------------------
# アクティビティログ管理関数
# --------------------------

def add_activity_log(user_id: int, activity: str, db):
    """アクティビティログを追加します。"""
    new_log = ActivityLog(
        user_id=user_id,
        activity=activity
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


def get_user_activities(user_id: int, db):
    """特定ユーザーのアクティビティログを取得します。"""
    return db.query(ActivityLog).filter(ActivityLog.user_id == user_id).order_by(ActivityLog.timestamp.desc()).all()


# --------------------------
# 画像分類結果管理関数
# --------------------------

def add_image_classification(user_id: int, image_path: str, classification_result: str, db):
    """画像分類結果を追加します。"""
    new_classification = ImageClassification(
        user_id=user_id,
        image_path=image_path,
        classification_result=classification_result
    )
    db.add(new_classification)
    db.commit()
    db.refresh(new_classification)
    return new_classification


def get_all_image_classifications(db):
    """すべての画像分類結果を取得します。"""
    return db.query(ImageClassification).order_by(ImageClassification.timestamp.desc()).all()


# --------------------------
# ユーザー設定管理関数
# --------------------------

def add_user_setting(user_id: int, db):
    """ユーザー設定を追加します。"""
    new_setting = UserSetting(
        user_id=user_id,
        notify_tts=True,
        notify_classification=True,
        notify_feedback=True
    )
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting


def get_user_settings(user_id: int, db):
    """ユーザー設定を取得します。"""
    return db.query(UserSetting).filter(UserSetting.user_id == user_id).first()


def update_user_settings(user_id: int, notify_tts: bool, notify_classification: bool, notify_feedback: bool, db):
    """ユーザー設定を更新します。"""
    setting = get_user_settings(user_id, db)
    if setting:
        setting.notify_tts = notify_tts
        setting.notify_classification = notify_classification
        setting.notify_feedback = notify_feedback
        db.commit()
        db.refresh(setting)
        return setting
    else:
        # 設定が存在しない場合は新規作成
        return add_user_setting(user_id, db)


# --------------------------
# 管理者権限チェック関数
# --------------------------

def is_admin_user(username: str, db) -> bool:
    """ユーザーが管理者であるかを確認します。"""
    user = get_user(username, db)
    if user:
        return user.is_admin
    return False


# --------------------------
# データベースの初期化スクリプト
# --------------------------

if __name__ == "__main__":
    """データベースを初期化します。"""
    init_db()
    print("Database initialized successfully.")
