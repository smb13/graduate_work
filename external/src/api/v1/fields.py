from typing import Annotated

from fastapi import Query

from core.config import settings

PageNumberQueryType = Annotated[int, Query(description="Pagination page number", ge=1)]
PageSizeQueryType = Annotated[int, Query(description="Pagination page size", ge=1, le=settings.page_size_max)]
