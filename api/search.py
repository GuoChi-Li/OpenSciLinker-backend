from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.dataSchema import get_db, Post, Tag, post_tags_table
from pydantic import BaseModel
from datetime import datetime
from typing import List, Any
from knowledge_graph.search_engine import JsonSearchEngine
from tqdm import tqdm

router = APIRouter()

search_engine = JsonSearchEngine()

TAGS_DICT = {}


def populate_tags_dict(session_maker):
    with session_maker() as session:
        # Fetch all posts
        posts = session.query(Post).all()

        # Populate the TAGS_DICT
        for post in tqdm(posts, desc="Processing TAGS_DICT"):
            for tag in post.tags:  # Changed here
                tag_name = tag.name  # Changed here
                if tag_name in TAGS_DICT:
                    TAGS_DICT[tag_name].append(post.id)
                else:
                    TAGS_DICT[tag_name] = [post.id]


########## Pydantic Models ##########


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    author_email: str
    tags: List[str]
    timestamp: datetime
    score: float = 0.0


class TagOut(BaseModel):
    tags: str


########## Utility Functions ##########
def convert_post_to_out(post: Post, score: float) -> PostOut:
    return PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        author_email=post.author_email,
        tags=[tag.name for tag in post.tags],
        timestamp=post.timestamp,
        score=score,
    )


def search_posts_by_tag(tag: str, db: Session = Depends(get_db)):
    # print(f"Searching for tag: {tag}")  # Print the tag for debugging
    post_ids = TAGS_DICT.get(tag, [])

    # Using the post_ids to fetch the actual Post objects
    # print(f"Found posts: {post_ids}")  # Print the posts for debugging

    # Convert these posts to PostOut
    # post_outs = [convert_post_to_out(post) for post in posts]
    return post_ids


# def get_post_by_id(post_id: int, db: Session = Depends(get_db)) -> Post:
#     print("post_id:", post_id)
#     print("db type:", type(db))
#     print("db:", db)
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=400, detail="Post not found")
#     return post

########## API Endpoints ##########


MAX_SEARCH_POSTS = 30
@router.get("/search/post/{query}")
def search_posts_by_query(query: str, db: Session = Depends(get_db)):
    tags, scores = search_engine.get_tags(query)
    print(f"input query: {query} get tags: {tags}")
    # print("get scores:", scores)
    post_id_score_table = {}
    for tag, score in zip(tags, scores):
        post_ids = search_posts_by_tag(tag)
        for post_id in post_ids:
            if post_id not in post_id_score_table:
                post_id_score_table[post_id] = score
            else:
                post_id_score_table[post_id] += score
    
    # get the top 30 posts
    top_post_ids = sorted(post_id_score_table.keys(), key=lambda x: post_id_score_table[x], reverse=True)[:MAX_SEARCH_POSTS]
    max_score = max([post_id_score_table[post_id] for post_id in top_post_ids])
    # print("Top post ids:", top_post_ids)
    # convert to List[PostOut]
    def get_post_by_id(post_id):
        post = db.query(Post).filter(Post.id == post_id).first()
        return post
    post_outs = [convert_post_to_out(get_post_by_id(post_id), post_id_score_table[post_id] / max_score) for post_id in top_post_ids]
    return post_outs



@router.get("/search/allTags")
def get_all_tags(db: Session = Depends(get_db)):
    # Fetch all tags from the database
    tags = db.query(Tag.name).all()
    # print(f"Queried tags: {tags}")  # DEBUG LINE

    # Convert the list of tuples to a list of TagOut models
    all_tags = [TagOut(tags=tag[0]) for tag in tags]
    return all_tags


@router.get("/posts/by-user/{user_email}", response_model=List[PostOut])
def get_posts_by_user_email(user_email: str, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.author_email == user_email).all()
    return [convert_post_to_out(post) for post in posts]
