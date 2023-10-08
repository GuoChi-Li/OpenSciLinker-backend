from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel

# Database configuration

DATABASE_URL = ""


# generate testdatabase
#DATABASE_URL = ""




engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


post_tags_table = Table(
    'post_tags', Base.metadata,
    Column('post_id', ForeignKey('posts.id'), primary_key=True),
    Column('tag_name', ForeignKey('tags.name'), primary_key=True) # Change here
)

# Database models
class User(Base):
    __tablename__ = "users"
    username = Column(String(20), index=True, nullable=False)
    email = Column(String(120), primary_key=True, unique=True, index=True, nullable=False)
    password = Column(String(60), nullable=False)
    posts = relationship("Post", back_populates="author")
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", backref="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    url = Column(String(100), nullable=False)
    author_email = Column(String(120), ForeignKey('users.email'), nullable=False)  # Reference 'email' instead of 'id'
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags_table, back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    user_email = Column(String(120), ForeignKey('users.email'), nullable=False)  # Reference 'email' instead of 'id'
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"
    user_email = Column(String(120), ForeignKey('users.email'), primary_key=True)  # Reference 'email' instead of 'id'
    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True)  # I added unique=True to ensure tag names are unique
    posts = relationship("Post", secondary=post_tags_table, back_populates="tags")


# Modify the Post model to establish a many-to-many relationship
Post.tags = relationship("Tag", secondary="post_tags", back_populates="posts")
Tag.posts = relationship("Post", secondary="post_tags", back_populates="tags")