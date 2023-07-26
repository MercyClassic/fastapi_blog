from sqlalchemy import select
from sqlalchemy.orm import joinedload, load_only, selectinload

from models.posts import Post, Tag
from models.users import User


query_with_prefetched_user_and_tags = (
    select(Post)
    .options(
        load_only(Post.id, Post.title, Post.content, Post.created_at, Post.published, Post.image),
    )
    .options(
        joinedload(Post.user)
        .options(load_only(User.id, User.username)),
    )
    .options(
        selectinload(Post.tags)
        .options(load_only(Tag.id, Tag.name, Tag.created_at)),
    )
)
