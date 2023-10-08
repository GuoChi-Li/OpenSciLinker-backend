from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.dataSchema import get_db, User, Post, Like, Comment, Tag
from pydantic import BaseModel
from datetime import datetime
from typing import List
from api.search import TAGS_DICT
from api.search import PostOut
from knowledge_graph.search_engine import JsonSearchEngine

router = APIRouter()

search_engine = JsonSearchEngine()


########## Pydantic Models ##########
class PostCreate(BaseModel):
    title: str
    content: str
    author_email: str  # We will use this to lookup the actual 'User' in the database
    tags: str # comma string
    url: str



class PostResponse(BaseModel):
    post_id: int
    title: str
    content: str
    author_username: str
    tags: List[str]
    timestamp: datetime
    message: str
    url:str


class LikeCreate(BaseModel):
    user_email: str
    post_id: int


class LikeResponse(BaseModel):
    user_email: str
    post_id: int
    message: str
    isLike: int = 0


class CommentCreate(BaseModel):
    user_email: str
    text: str
    post_id: int


class CommentCreateResponse(BaseModel):
    comment_id: int
    text: str
    user_email: str
    timestamp: datetime
    message: str


class CommentOut(BaseModel):
    comment_id: int
    text: str
    user_email: str
    timestamp: datetime


########## Utility Functions ##########


def get_user_by_email(email: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


def get_or_create_like(user_email: str, post_id: int, db: Session):
    existing_like = (
        db.query(Like).filter_by(user_email=user_email, post_id=post_id).first()
    )
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return False
    else:
        new_like = Like(user_email=user_email, post_id=post_id)
        db.add(new_like)
        db.commit()
        return True


def get_or_create_tag(tag_name: str, db: Session) -> Tag:
    """Retrieve an existing tag or create a new one."""
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        db.flush()  # We're using flush here to make sure the tag is added to the session but not committed yet
    return tag


def auto_tagging(title, content):
    input_query = title + " " + content
    tags, scores = search_engine.get_tags(input_query)
    return tags


########## API Endpoints ##########
@router.post("/posts", response_model=PostResponse)
def write_post(post_data: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    # get authror name
    author = get_user_by_email(post_data.author_email, db)
    author_name = author.username

    tags_split_list_w = post_data.tags.split(',')
    tags_split_list = [item.strip() for item in tags_split_list_w]
    # Create the post without tags for now
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        author_email=post_data.author_email,
        url=post_data.url,
        timestamp= str(datetime.now())
    )

    if len(post_data.tags) > 0:
        selected_tags = tags_split_list
    else:
        selected_tags = auto_tagging(post_data.title, content=post_data.content)

    db.add(new_post)
    db.flush()  # This will allow us to get the id of new_post without committing the transaction

    # Get or create each tag and associate it with the post
    for tag_name in selected_tags:
        tag = get_or_create_tag(tag_name, db)
        new_post.tags.append(tag)

    # update the TAGS_DICT with this post's ID
    for tag_name in post_data.tags:
        if tag_name in TAGS_DICT:
            TAGS_DICT[tag_name].append(new_post.id)
        else:
            TAGS_DICT[tag_name] = [new_post.id]

    db.commit()  # Now we commit the transaction after all database interactions

    return PostResponse(
        post_id=new_post.id,
        title=new_post.title,
        content=new_post.content,
        author_username=author_name,
        tags=[tag.name for tag in new_post.tags],
        timestamp=new_post.timestamp,
        message="Post successfully created",
        url=new_post.url
    )


@router.post("/posts/like", response_model=LikeResponse)
def like_post(like_data: LikeCreate, db: Session = Depends(get_db)) -> LikeResponse:
    """Endpoint to like or unlike a post."""
    post_id = like_data.post_id  # Extract the post_id from the request body

    is_liked = get_or_create_like(like_data.user_email, post_id, db)

    if is_liked:
        return LikeResponse(
            user_email=like_data.user_email,
            post_id=post_id,
            message="Liked the post",
            isLike=1,
        )
    else:
        return LikeResponse(
            user_email=like_data.user_email,
            post_id=post_id,
            message="Unliked the post",
            isLike=0,
        )


@router.post("/posts/comments", response_model=CommentCreateResponse)
def add_comment_to_post(
    comment_data: CommentCreate, db: Session = Depends(get_db)
) -> CommentCreateResponse:
    """Endpoint to leave a comment on a specific post."""
    post_id = comment_data.post_id  # Extract the post_id from the request body

    new_comment = Comment(
        text=comment_data.text,
        timestamp=datetime.now(),
        user_email=comment_data.user_email,
        post_id=post_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentCreateResponse(
        comment_id=new_comment.id,
        text=new_comment.text,
        user_email=comment_data.user_email,
        timestamp=new_comment.timestamp,
        message="Comment successfully added",
    )


@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
def get_comments_for_post(
    post_id: int, db: Session = Depends(get_db)
) -> List[CommentOut]:
    """Endpoint to get all comments for a specific post."""
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    if not comments:
        raise HTTPException(status_code=404, detail="No comments found for this post")

    return [
        CommentOut(
            comment_id=comment.id,
            text=comment.text,
            user_email=comment.user_email,
            timestamp=comment.timestamp,
        )
        for comment in comments
    ]


@router.get("/posts/{post_id}", response_model=PostOut)
def get_post_by_id_endpoint(post_id: int, db: Session = Depends(get_db)) -> PostOut:
    """Endpoint to retrieve a post by its ID."""
    print("db:", db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    tag_names = [tag.name for tag in post.tags]
    print('POST TITLE:',post.title)

    return PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        author_email=post.author_email,
        tags=tag_names,
        timestamp=post.timestamp,
    )
