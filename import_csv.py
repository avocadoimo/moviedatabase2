import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

# Flask アプリ作成（新しいDBに切り替え）
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_new.db'
db = SQLAlchemy(app)

# 映画モデル定義（拡張版）
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    year = db.Column(db.Integer)
    release_date = db.Column(db.String(20))
    title = db.Column(db.String(200))
    revenue = db.Column(db.Float)
    category = db.Column(db.String(10))
    distributor = db.Column(db.String(100))
    description = db.Column(db.Text)
    director = db.Column(db.String(200))
    author = db.Column(db.String(200))
    actor = db.Column(db.String(500))
    scriptwriter = db.Column(db.String(200))
    producer = db.Column(db.String(200))
    copyright = db.Column(db.String(200))
    genre = db.Column(db.String(200))

with app.app_context():
    csv_path = r"C:\Users\2501016\Box\0000_マイフォルダ\自習用\movie_app ver.2\【詳細付き】興行収入データベース（2000-2024年）.csv"

    print("✅ 現在の作業フォルダ:", os.getcwd())
    print("✅ 読み込むCSVファイル:", csv_path)

    # 新しいデータベースを初期化
    db.drop_all()
    db.create_all()

    # CSV読み込み
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='shift_jis')
    except FileNotFoundError:
        print("❌ ファイルが見つかりません。パスを確認してください。")
        exit()

    added = 0
    skipped = 0
    for _, row in df.iterrows():
        if pd.isna(row['年']) or pd.isna(row['作品名']) or pd.isna(row['興収(億円)']):
            skipped += 1
            continue

        movie = Movie(
            movie_id=int(row.get('映画ID', 0)),
            year=int(row['年']),
            release_date=row.get('公開日', ''),
            title=row['作品名'],
            revenue=float(row['興収(億円)']),
            category=row.get('区分', ''),
            distributor=row.get('配給会社', ''),
            description=row.get('あらすじ', ''),
            director=row.get('監督', ''),
            author=row.get('脚本', ''),
            actor=row.get('キャスト', ''),
            scriptwriter=row.get('脚本家', ''),
            producer=row.get('プロデューサー', ''),
            copyright=row.get('コピーライト', '')
        )
        db.session.add(movie)
        added += 1

    db.session.commit()
    print(f"✅ 新しいDB（movie_new.db）に取り込み完了：追加 {added} 件、スキップ {skipped} 件")
