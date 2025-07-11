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
    genre = db.Column(db.String(200))  # ジャンル列を追加

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

    # CSVの列名を確認
    print("📊 CSVの列名:")
    for i, col in enumerate(df.columns):
        print(f"  {i+1}: {col}")

    added = 0
    skipped = 0
    
    for _, row in df.iterrows():
        if pd.isna(row['年']) or pd.isna(row['作品名']) or pd.isna(row['興収(億円)']):
            skipped += 1
            continue

        # ジャンルの処理（複数のCSV列名パターンに対応）
        genre_value = ''
        possible_genre_columns = ['ジャンル', 'genre', 'Genre', 'GENRE']
        
        for col in possible_genre_columns:
            if col in df.columns and not pd.isna(row.get(col)):
                genre_value = str(row.get(col, '')).strip()
                break
        
        # ジャンルが空の場合はカテゴリから推測
        if not genre_value and not pd.isna(row.get('区分')):
            category = str(row.get('区分', '')).strip()
            if category == '邦画':
                genre_value = '日本映画'
            elif category == '洋画':
                genre_value = '外国映画'

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
            copyright=row.get('コピーライト', ''),
            genre=genre_value  # ジャンル情報を追加
        )
        db.session.add(movie)
        added += 1

    db.session.commit()
    print(f"✅ 新しいDB（movie_new.db）に取り込み完了：追加 {added} 件、スキップ {skipped} 件")
    
    # ジャンル情報の確認
    print("\n📊 ジャンル情報の統計:")
    genre_stats = db.session.query(Movie.genre, db.func.count(Movie.id)).group_by(Movie.genre).all()
    for genre, count in genre_stats:
        if genre:
            print(f"  {genre}: {count} 件")
    
    # ジャンルなしの映画数
    no_genre_count = Movie.query.filter(Movie.genre.is_(None) | (Movie.genre == '')).count()
    print(f"  ジャンル未設定: {no_genre_count} 件")