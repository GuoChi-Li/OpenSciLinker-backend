from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataSchema import User, Post, Comment, Like, Tag, get_db
from passlib.context import CryptContext
import random
import string
import datetime

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Set up database
#DATABASE_URL = ""
DATABASE_URL = ""
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)



from dataSchema import Base, engine

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Generate random string
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


# Define a list of tags
tags = ["Technology", "Science", "Programming", "Art", "Travel", "Food", "Music", "Sports", "Fashion", "Health"]

try:
    with SessionLocal() as session:
        users = []  # To store user objects for referencing later
        # Create 10 user records
        for _ in range(10):
            username = generate_random_string(8)
            email = generate_random_string(8) + "@example.com"
            raw_password = generate_random_string(8) 
            hashed_password = get_password_hash(raw_password)
            
            user = User(username=username, email=email, password=hashed_password)
            users.append(user)
            session.add(user)

            # Create posts for this user
            for _ in range(3):  # Each user gets 3 posts
                post = Post(
                    title=generate_random_string(15),
                    content=generate_random_string(100),
                    timestamp=datetime.datetime.now(),
                    author_email=email
                )
                user.posts.append(post)  # Add post to user's posts
                session.add(post)
                
                # Randomly assign a tag to this post
                tag_name = random.choice(tags)
                
                # Check if the tag already exists in the database
                existing_tag = session.query(Tag).filter_by(name=tag_name).first()
                if existing_tag is None:
                    # Tag doesn't exist, create and add it to the session
                    tag = Tag(name=tag_name)
                    session.add(tag)
                else:
                    # Tag already exists, use the existing one
                    tag = existing_tag
                
                post.tags.append(tag)
                
        # Commit users, posts, and tags first to generate IDs
        session.commit()

        for user in users:
            for post in user.posts:
                # Create comments for this post
                for _ in range(2):  # Each post gets 2 comments
                    comment = Comment(
                        text=generate_random_string(50),
                        timestamp=datetime.datetime.now(),
                        user_email=user.email,
                        post_id=post.id
                    )
                    session.add(comment)
                
                # Create likes for this post
                like = Like(user_email=user.email, post_id=post.id)
                session.add(like)
                
        session.commit()

except Exception as e:
    print(f"Error occurred: {e}")