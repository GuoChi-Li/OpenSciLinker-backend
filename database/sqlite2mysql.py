from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataSchema import User, Base, Post, Comment, Tag, Like

# Database connection URLs
DATABASE_URL_SQLITE = ""
DATABASE_URL_MYSQL = ""

# Creating engine for both SQLite and MySQL databases
sqlite_engine = create_engine(DATABASE_URL_SQLITE)
mysql_engine = create_engine(DATABASE_URL_MYSQL)

# Session makers for both SQLite and MySQL databases
SessionLocal_sqlite = sessionmaker(bind=sqlite_engine)
SessionLocal_mysql = sessionmaker(bind=mysql_engine)

# Creating tables for MySQL database
Base.metadata.create_all(bind=mysql_engine)

# Migrating User data from SQLite to MySQL
with SessionLocal_sqlite() as session_sqlite, SessionLocal_mysql() as session_mysql:
    users = session_sqlite.query(User).all()
    for user in users:
        existing_user = session_mysql.query(User).filter_by(email=user.email).first()
        if not existing_user:
            session_mysql.add(User(
                username=user.username,
                email=user.email,
                password=user.password
            ))
    session_mysql.commit()

# Migrating Tag data
with SessionLocal_sqlite() as session_sqlite, SessionLocal_mysql() as session_mysql:
    tags = session_sqlite.query(Tag).all()
    for tag in tags:
        existing_tag = session_mysql.query(Tag).filter_by(name=tag.name).first()
        if not existing_tag:
            session_mysql.add(Tag(name=tag.name))
    session_mysql.commit()

# Migrating Post data and their associated tags
with SessionLocal_sqlite() as session_sqlite, SessionLocal_mysql() as session_mysql:
    posts = session_sqlite.query(Post).all()
    for post in posts:
        new_post = Post(
            title=post.title,
            content=post.content,
            timestamp=post.timestamp,
            author_email=post.author_email
        )
        sqlite_tags = session_sqlite.query(Tag).filter(Tag.posts.any(id=post.id)).all()
        new_post.tags = [session_mysql.query(Tag).filter_by(name=tag.name).first() for tag in sqlite_tags]
        session_mysql.add(new_post)
    session_mysql.commit()

# Migrating Comment data
with SessionLocal_sqlite() as session_sqlite, SessionLocal_mysql() as session_mysql:
    comments = session_sqlite.query(Comment).all()
    for comment in comments:
        session_mysql.add(Comment(
            text=comment.text,
            timestamp=comment.timestamp,
            user_email=comment.user_email,
            post_id=comment.post_id
        ))
    session_mysql.commit()

# Migrating Like data
with SessionLocal_sqlite() as session_sqlite, SessionLocal_mysql() as session_mysql:
    likes = session_sqlite.query(Like).all()
    for like in likes:
        session_mysql.add(Like(
            user_email=like.user_email,
            post_id=like.post_id
        ))
    session_mysql.commit()

# Migrating Post-Tag relationships
with SessionLocal_sqlite() as session_sqlite, SessionLocal_mysql() as session_mysql:
    posts = session_sqlite.query(Post).all()
    for post in posts:
        mysql_post = session_mysql.query(Post).filter_by(title=post.title, author_email=post.author_email).first()
        if mysql_post:
            post_tags = session_sqlite.query(Tag).filter(Tag.posts.any(id=post.id)).all()
            for tag in post_tags:
                mysql_tag = session_mysql.query(Tag).filter_by(name=tag.name).first()
                if mysql_tag and mysql_tag not in mysql_post.tags:
                    mysql_post.tags.append(mysql_tag)
    session_mysql.commit()

print("Data migration completed.")
