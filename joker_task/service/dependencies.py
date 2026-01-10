from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import User
from joker_task.interfaces.interfaces import (
    MapperInterface,
    TagControllerInterface,
    TaskCollectorInterface,
    WorkbenchControllerInterface,
)
from joker_task.schemas import Filter
from joker_task.service.mapper import Mapper
from joker_task.service.security import get_user
from joker_task.service.tags_controler import TagController
from joker_task.service.task_collector import TaskCollector
from joker_task.service.workbench_controler import WorkbenchController

T_CollectorTask = Annotated[TaskCollectorInterface, Depends(TaskCollector)]
T_Filter = Annotated[Filter, Query()]
T_Mapper = Annotated[MapperInterface, Depends(Mapper)]
T_OAuth2PRF = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_TagController = Annotated[TagControllerInterface, Depends(TagController)]
T_User = Annotated[User, Depends(get_user)]
T_WorkbenchController = Annotated[
    WorkbenchControllerInterface, Depends(WorkbenchController)
]
