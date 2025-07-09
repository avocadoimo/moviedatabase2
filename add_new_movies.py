import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

# Flask アプリ作成
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
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

# 実行ブロック
with app.app_context():
    new_csv_path = r"C:\Users\2501016\Box\0000_マイフォルダ\自習用\movie_app\【詳細付き】興行収入データベース（2000-2024年）.csv"

    print("✅ 現在の作業フォルダ:", os.getcwd())
    print("✅ 新規CSVファイル:", new_csv_path)

    try:
        df = pd.read_csv(new_csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(new_csv_path, encoding='shift_jis')
    except FileNotFoundError:
        print("❌ ファイルが見つかりません。パスを確認してください。")
        exit()

    added = 0
    updated = 0
    skipped = 0
    deleted_titles = []

    for _, row in df.iterrows():
        if pd.isna(row['年']) or pd.isna(row['作品名']) or pd.isna(row['興収(億円)']):
            skipped += 1
            continue

        title = str(row['作品名']).strip()
        revenue = float(row['興収(億円)'])
        movie_id = int(row.get('映画ID', 0))

        # タイトルと興収が一致する作品を削除
        duplicates = Movie.query.filter_by(title=title, revenue=revenue).all()
        if duplicates:
            for d in duplicates:
                db.session.delete(d)
            deleted_titles.append(title)

        # 映画IDが一致する場合は上書き
        existing = Movie.query.filter_by(movie_id=movie_id).first()
        if existing:
            existing.year = int(row['年'])
            existing.release_date = row.get('公開日', '')
            existing.title = title
            existing.revenue = revenue
            existing.category = row.get('区分', '')
            existing.distributor = row.get('配給会社', '')
            existing.description = row.get('あらすじ', '')
            existing.director = row.get('監督', '')
            existing.author = row.get('脚本', '')
            existing.actor = row.get('キャスト', '')
            existing.scriptwriter = row.get('脚本家', '')
            existing.producer = row.get('プロデューサー', '')
            existing.copyright = row.get('コピーライト', '')
            updated += 1
        else:
            movie = Movie(
                movie_id=movie_id,
                year=int(row['年']),
                release_date=row.get('公開日', ''),
                title=title,
                revenue=revenue,
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

    print(f"✅ 映画データを取り込みました（追加: {added} 件、更新: {updated} 件、スキップ: {skipped} 件）")

    if deleted_titles:
        print("\n🗑️ タイトル + 興収 が一致したため削除されたデータ:")
        for title in deleted_titles:
            print("・", title)
