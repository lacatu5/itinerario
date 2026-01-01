from core.exceptions import AuthorizationException


def verify_ownership(
    resource_owner_id: int | str, current_user_id: int | str, resource_type: str = "resource"
):
    if str(resource_owner_id) != str(current_user_id):
        raise AuthorizationException(f"Not authorized to modify this {resource_type}")


def verify_participation(
    participants: list, current_user_id: int | str, resource_type: str = "resource"
):
    if current_user_id not in participants:
        raise AuthorizationException(f"User is not a participant in this {resource_type}")
