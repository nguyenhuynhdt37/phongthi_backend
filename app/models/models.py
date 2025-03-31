from typing import List, Optional

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, String, TIMESTAMP, Time, text
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Departments(Base):
    __tablename__ = 'departments'
    __table_args__ = (
        Index('name', 'name', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    instructors: Mapped[List['Instructors']] = relationship('Instructors', back_populates='department')
    students: Mapped[List['Students']] = relationship('Students', back_populates='department')


class Exams(Base):
    __tablename__ = 'exams'
    __table_args__ = (
        CheckConstraint('(`credits` > 0)', name='exams_chk_1'),
        CheckConstraint('(`exam_duration` > 0)', name='exams_chk_2'),
        Index('course_code', 'course_code', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_code: Mapped[str] = mapped_column(String(20))
    course_name: Mapped[str] = mapped_column(String(100))
    credits: Mapped[int] = mapped_column(Integer)
    exam_duration: Mapped[int] = mapped_column(Integer)

    exam_schedule: Mapped[List['ExamSchedule']] = relationship('ExamSchedule', back_populates='exam')


class HocPhan(Base):
    __tablename__ = 'hoc_phan'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    so_tin_chi: Mapped[int] = mapped_column(Integer)
    ma_hoc_phan: Mapped[str] = mapped_column(String(20))
    ten_hoc_phan: Mapped[str] = mapped_column(String(255))
    phan_ky: Mapped[int] = mapped_column(Integer)


class Rooms(Base):
    __tablename__ = 'rooms'
    __table_args__ = (
        CheckConstraint('(`capacity` > 0)', name='rooms_chk_1'),
        Index('room_code', 'room_code', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_code: Mapped[str] = mapped_column(String(20))
    capacity: Mapped[int] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(Enum('available', 'in_use', 'maintenance'), server_default=text("'available'"))

    exam_schedule: Mapped[List['ExamSchedule']] = relationship('ExamSchedule', back_populates='room')
    camera_records: Mapped[List['CameraRecords']] = relationship('CameraRecords', back_populates='room')


class Tblrole(Base):
    __tablename__ = 'tblrole'
    __table_args__ = (
        Index('tblRole_unique', 'role_name', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(100))
    create_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    tbluser: Mapped[List['Tbluser']] = relationship('Tbluser', back_populates='role')


class ThoiGianThi(Base):
    __tablename__ = 'thoi_gian_thi'

    so_tin: Mapped[int] = mapped_column(Integer, primary_key=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer)


class Tbluser(Base):
    __tablename__ = 'tbluser'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['tblrole.id'], name='tbluser_tblrole_FK'),
        Index('tbluser_tblrole_FK', 'role_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    password: Mapped[Optional[str]] = mapped_column(String(100))
    create_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    avatar: Mapped[Optional[str]] = mapped_column(VARCHAR(500))

    role: Mapped['Tblrole'] = relationship('Tblrole', back_populates='tbluser')
    instructors: Mapped[List['Instructors']] = relationship('Instructors', back_populates='user')
    students: Mapped[List['Students']] = relationship('Students', back_populates='user')
    tblsesson: Mapped[List['Tblsesson']] = relationship('Tblsesson', back_populates='user')


class Instructors(Base):
    __tablename__ = 'instructors'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL', name='instructors_ibfk_2'),
        ForeignKeyConstraint(['user_id'], ['tbluser.id'], ondelete='CASCADE', name='instructors_ibfk_1'),
        Index('department_id', 'department_id'),
        Index('email', 'email', unique=True),
        Index('instructor_code', 'instructor_code', unique=True),
        Index('user_id', 'user_id', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instructor_code: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    department_id: Mapped[Optional[int]] = mapped_column(Integer)

    department: Mapped[Optional['Departments']] = relationship('Departments', back_populates='instructors')
    user: Mapped[Optional['Tbluser']] = relationship('Tbluser', back_populates='instructors')
    exam_schedule: Mapped[List['ExamSchedule']] = relationship('ExamSchedule', foreign_keys='[ExamSchedule.instructor_1]', back_populates='instructors')
    exam_schedule_: Mapped[List['ExamSchedule']] = relationship('ExamSchedule', foreign_keys='[ExamSchedule.instructor_2]', back_populates='instructors_')


class Students(Base):
    __tablename__ = 'students'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL', name='students_ibfk_2'),
        ForeignKeyConstraint(['user_id'], ['tbluser.id'], ondelete='CASCADE', name='students_ibfk_1'),
        Index('department_id', 'department_id'),
        Index('email', 'email', unique=True),
        Index('student_code', 'student_code', unique=True),
        Index('user_id', 'user_id', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_code: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    birth_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    department_id: Mapped[Optional[int]] = mapped_column(Integer)

    department: Mapped[Optional['Departments']] = relationship('Departments', back_populates='students')
    user: Mapped[Optional['Tbluser']] = relationship('Tbluser', back_populates='students')
    camera_records: Mapped[List['CameraRecords']] = relationship('CameraRecords', back_populates='student')
    student_exams: Mapped[List['StudentExams']] = relationship('StudentExams', back_populates='student')


class Tblsesson(Base):
    __tablename__ = 'tblsesson'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['tbluser.id'], name='tblsesson_tbluser_FK'),
        Index('tblsesson_tbluser_FK', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    token: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    ip_address: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    login_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    logout_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    is_trusted: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    approval_code: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    approval_expires: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    device_info: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    location_city: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    location_country: Mapped[Optional[str]] = mapped_column(VARCHAR(255))

    user: Mapped[Optional['Tbluser']] = relationship('Tbluser', back_populates='tblsesson')


class ExamSchedule(Base):
    __tablename__ = 'exam_schedule'
    __table_args__ = (
        ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE', name='exam_schedule_ibfk_1'),
        ForeignKeyConstraint(['instructor_1'], ['instructors.id'], ondelete='CASCADE', name='exam_schedule_ibfk_3'),
        ForeignKeyConstraint(['instructor_2'], ['instructors.id'], ondelete='CASCADE', name='exam_schedule_ibfk_4'),
        ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE', name='exam_schedule_ibfk_2'),
        Index('exam_id', 'exam_id'),
        Index('instructor_1', 'instructor_1'),
        Index('instructor_2', 'instructor_2'),
        Index('room_id', 'room_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer)
    room_id: Mapped[int] = mapped_column(Integer)
    exam_date: Mapped[datetime.date] = mapped_column(Date)
    start_time: Mapped[datetime.time] = mapped_column(Time)
    end_time: Mapped[datetime.time] = mapped_column(Time)
    instructor_1: Mapped[int] = mapped_column(Integer)
    instructor_2: Mapped[int] = mapped_column(Integer)

    exam: Mapped['Exams'] = relationship('Exams', back_populates='exam_schedule')
    instructors: Mapped['Instructors'] = relationship('Instructors', foreign_keys=[instructor_1], back_populates='exam_schedule')
    instructors_: Mapped['Instructors'] = relationship('Instructors', foreign_keys=[instructor_2], back_populates='exam_schedule_')
    room: Mapped['Rooms'] = relationship('Rooms', back_populates='exam_schedule')
    camera_records: Mapped[List['CameraRecords']] = relationship('CameraRecords', back_populates='exam_schedule')
    student_exams: Mapped[List['StudentExams']] = relationship('StudentExams', back_populates='exam_schedule')


class CameraRecords(Base):
    __tablename__ = 'camera_records'
    __table_args__ = (
        ForeignKeyConstraint(['exam_schedule_id'], ['exam_schedule.id'], ondelete='CASCADE', name='camera_records_ibfk_2'),
        ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE', name='camera_records_ibfk_3'),
        ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE', name='camera_records_ibfk_1'),
        Index('exam_schedule_id', 'exam_schedule_id'),
        Index('room_id', 'room_id'),
        Index('student_id', 'student_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer)
    exam_schedule_id: Mapped[int] = mapped_column(Integer)
    room_id: Mapped[int] = mapped_column(Integer)
    face_recognition_status: Mapped[str] = mapped_column(Enum('verified', 'unverified'))
    timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    exam_schedule: Mapped['ExamSchedule'] = relationship('ExamSchedule', back_populates='camera_records')
    room: Mapped['Rooms'] = relationship('Rooms', back_populates='camera_records')
    student: Mapped['Students'] = relationship('Students', back_populates='camera_records')


class StudentExams(Base):
    __tablename__ = 'student_exams'
    __table_args__ = (
        ForeignKeyConstraint(['exam_schedule_id'], ['exam_schedule.id'], ondelete='CASCADE', name='student_exams_ibfk_2'),
        ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE', name='student_exams_ibfk_1'),
        Index('exam_schedule_id', 'exam_schedule_id'),
        Index('student_id', 'student_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer)
    exam_schedule_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(Enum('registered', 'attended', 'absent'), server_default=text("'registered'"))

    exam_schedule: Mapped['ExamSchedule'] = relationship('ExamSchedule', back_populates='student_exams')
    student: Mapped['Students'] = relationship('Students', back_populates='student_exams')
