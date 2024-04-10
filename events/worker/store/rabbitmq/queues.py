from enum import Enum

from store.models import ChannelType


class Actions(Enum):
    REVIEW_LIKE = "review_like"
    WEEKLY_BOOKMARKS = "weekly_bookmarks"
    GENERAL_NOTICE = "general_notice"


class RmqQueue(Enum):
    PUSH_REVIEW_LIKE = ChannelType.PUSH.value + "." + Actions.REVIEW_LIKE.value
    EMAIL_WEEKLY_BOOKMARKS = ChannelType.EMAIL.value + "." + Actions.WEEKLY_BOOKMARKS.value
    PUSH_GENERAL_NOTICE = ChannelType.PUSH.value + "." + Actions.GENERAL_NOTICE.value
    EMAIL_GENERAL_NOTICE = ChannelType.EMAIL.value + "." + Actions.GENERAL_NOTICE.value


def get_rmq_queues_list():
    return [
        ChannelType.PUSH.value + "." + Actions.REVIEW_LIKE.value,
        ChannelType.EMAIL.value + "." + Actions.WEEKLY_BOOKMARKS.value,
        ChannelType.PUSH.value + "." + Actions.GENERAL_NOTICE.value,
        ChannelType.EMAIL.value + "." + Actions.GENERAL_NOTICE.value,
    ]
