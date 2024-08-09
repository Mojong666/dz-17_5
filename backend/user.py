from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from slugify import slugify

from backend.db_depends import get_db
from backend.schemas import CreateUser, UpdateUser
from backend.models import User, Task

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
def all_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User)).all()
    return users


@router.get('/{user_id}')
def user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user


@router.post('/create')
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    new_user = User(**user.dict(), slug=slugify(user.username))
    db.add(new_user)
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    stmt = update(User).where(User.id == user_id).values(**user.dict())
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete('/delete')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Delete all related tasks first
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()

    stmt = delete(User).where(User.id == user_id)
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User deleted successfully'}


@router.get('/{user_id}/tasks')
def tasks_by_user_id(user_id: int, db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task).filter(Task.user_id == user_id)).all()
    return tasks
