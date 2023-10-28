from services.tags import TagService


def get_tag_service() -> TagService:
    return TagService()
