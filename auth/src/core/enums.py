from enum import Enum


class SystemRolesEnum(str, Enum):
    user = "user"
    admin = "admin"


class ActionEnum(str, Enum):
    user_create = "user:create"
    user_read = "user:read"
    user_update = "user:update"
    user_delete = "user:delete"

    role_create = "role:create"
    role_read = "role:read"
    role_update = "role:update"
    role_delete = "role:delete"
    role_permission_create = "role.permission:create"
    role_permission_read = "role.permission:read"
    role_permission_update = "role.permission:update"
    role_permission_delete = "role.permission:delete"
    role_binding_create = "role.binding:create"
    role_binding_read = "role.binding:read"
    role_binding_update = "role.binding:update"
    role_binding_delete = "role.binding:delete"

    me_register = "me:register"
    me_read = "me:read"
    me_update = "me:update"
    me_delete = "me:delete"
    me_change_password = "me:change_password"
    me_change_login = "me:change_login"
    me_access_log = "me:access_log"

    @classmethod
    def me_actions(cls) -> list["ActionEnum"]:
        return [
            cls.me_register,
            cls.me_read,
            cls.me_update,
            cls.me_delete,
            cls.me_change_password,
            cls.me_change_login,
            cls.me_access_log,
        ]

    @classmethod
    def user_actions(cls) -> list["ActionEnum"]:
        return [
            cls.user_create,
            cls.user_read,
            cls.user_update,
            cls.user_delete,
        ]

    @classmethod
    def role_actions(cls) -> list["ActionEnum"]:
        return [
            cls.role_create,
            cls.role_read,
            cls.role_update,
            cls.role_delete,
            cls.role_permission_create,
            cls.role_permission_read,
            cls.role_permission_update,
            cls.role_permission_delete,
            cls.role_binding_create,
            cls.role_binding_read,
            cls.role_binding_update,
            cls.role_binding_delete,
        ]
