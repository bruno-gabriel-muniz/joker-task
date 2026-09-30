from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import User
from joker_task.interfaces.interfaces import (
    MapperInterface,
    TagServiceInterface,
    TaskCollectorInterface,
    ViewServiceInterface,
    WorkbenchServiceInterface,
)
from joker_task.schemas import FilterSchema
from joker_task.service.mapper import Mapper
from joker_task.service.security import get_user
from joker_task.service.tags_service import TagService
from joker_task.service.task_collector import TaskCollector
from joker_task.service.view_service import ViewService
from joker_task.service.workbench_service import WorkbenchService

T_CollectorTask = Annotated[TaskCollectorInterface, Depends(TaskCollector)]
T_Filter = Annotated[FilterSchema, Query()]
T_Mapper = Annotated[MapperInterface, Depends(Mapper)]
T_OAuth2PRF = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_TagService = Annotated[TagServiceInterface, Depends(TagService)]
T_ViewService = Annotated[ViewServiceInterface, Depends(ViewService)]
T_WorkbenchService = Annotated[
    WorkbenchServiceInterface, Depends(WorkbenchService)
]
T_User = Annotated[User, Depends(get_user)]
