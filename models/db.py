# pylint: disable=too-few-public-methods

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    email = Column(String(255))
    role = Column(String(255), default='user')
    submissions = relationship('Submission', back_populates='user')
    wireguard_profiles = relationship('WireguardProfile', back_populates='user')

class Problem(Base):
    __tablename__ = 'problems'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_valid = Column(Boolean, default=True)
    allow_submission = Column(Boolean, default=False)
    problem_name = Column(String(255))
    created_time = Column(TIMESTAMP, default=func.now)
    start_time = Column(DateTime)
    deadline = Column(DateTime)
    submissions = relationship('Submission', back_populates='problem')
    subtasks = relationship('Subtask', back_populates='problem')
    playbooks = relationship('SubtaskPlaybook', back_populates='problem')

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    problem_id = Column(Integer, ForeignKey('problems.id'))
    submission_score = Column(Integer)
    submit_time = Column(TIMESTAMP, default=func.now)
    user = relationship('User', back_populates='submissions')
    problem = relationship('Problem', back_populates='submissions')

class Subtask(Base):
    __tablename__ = 'subtasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey('problems.id'))
    task_name = Column(String(255))
    points = Column(Integer)
    is_valid = Column(Boolean, default=True)
    problem = relationship('Problem', back_populates='subtasks')
    subtask_results = relationship('SubtaskResult', back_populates='subtask')

class WireguardProfile(Base):
    __tablename__ = 'wireguard_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_valid = Column(Boolean, default=True)
    creation_date_time = Column(TIMESTAMP, default=func.now)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='wireguard_profiles')

class SubtaskResult(Base):
    __tablename__ = 'subtask_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'))
    task_id = Column(Integer, ForeignKey('subtasks.id'))
    is_passed = Column(Boolean)
    points = Column(Integer)
    subtask = relationship('Subtask', back_populates='subtask_results')

class SubtaskDependency(Base):
    __tablename__ = 'subtask_dependencies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_task_id = Column(Integer, ForeignKey('subtasks.id'))
    child_task_id = Column(Integer, ForeignKey('subtasks.id'))

class SubtaskPlaybook(Base):
    __tablename__ = 'subtask_playbooks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey('problems.id'))
    is_valid = Column(Boolean, default=True)
    playbook_name = Column(String(255))
    problem = relationship('Problem', back_populates='playbooks')
