from services.posts import PostService


def get_post_service() -> PostService:
    return PostService()
