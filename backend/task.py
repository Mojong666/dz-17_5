from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from slugify import slugify

from backend.db_depends import get_db
from backend.schemas import CreateTask, UpdateTask
from backend.models import Task, User

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
def all_tasks(db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/{task_id}')
def task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(Task).filter(Task.id == task_id)).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task was not found")
    return task


@router.post('/create')
def create_task(task: CreateTask, user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    new_task = Task(**task.dict(), user_id=user_id, slug=slugify(task.title))
    db.add(new_task)
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
def update_task(task_id: int, task: UpdateTask, db: Session = Depends(get_db)):
    stmt = update(Task).where(Task.id == task_id).values(**task.dict())
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task was not found")
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task update is successful!'}


@router.delete('/delete')
def delete_task(task_id: int, db: Session = Depends(get_db)):
    stmt = delete(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task was not found")
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task deleted successfully'}
