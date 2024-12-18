from sqlalchemy import Column, Integer, String, create_engine, Boolean, DateTime, ForeignKey, Table, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

class LearningState:
    NOT_LEARNING = 0
    LEARNING = 1
    LEARNING_PROBLEMATIC = 2
    LEARNED = 3
    ALREADY_KNOWN = 4
    
    
    def __str__(self):
        # Настроенные строки для каждого состояния
        state_descriptions = {
            LearningState.NOT_LEARNING: "Not Learning",
            LearningState.LEARNING: "Learning",
            LearningState.LEARNING_PROBLEMATIC: "Learning and Problematic",
            LearningState.LEARNED: "Learned",
            LearningState.ALREADY_KNOWN: "Already Known"
        }
        return state_descriptions.get(self, "Unknown State")

Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)

word_category_association = Table(
    'word_category_association', Base.metadata,
    Column('word_id', Integer, ForeignKey('words.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


user_category_association = Table(
    'user_category_association', Base.metadata,
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# word_example_association = Table(
#     'word_example_association', Base.metadata,
#     Column('word_id', Integer, ForeignKey('words.id'), primary_key=True),
#     Column('example_id', Integer, ForeignKey('examples.id'), primary_key=True)
# )



class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True, autoincrement=True)
    english = Column(String, nullable=False)
    russian = Column(String, nullable=False)
    transcription = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
    
    categories = relationship('Category', secondary=word_category_association, back_populates='words')
    examples = relationship("Example", back_populates="word")
    # examples = relationship('Example', secondary=word_example_association, back_populates='words')
    
    

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    creation_date = Column(DateTime, server_default=func.now(), nullable=False)
    is_admin = Column(Boolean, default=False)
    
    categories = relationship('Category', secondary=user_category_association, back_populates='users')

class Stats(Base):
    __tablename__ = "stats"
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False, primary_key=True)
    learned_words = Column(Integer, nullable=False, default=0)
    learning_words = Column(Integer, nullable=False, default=0)
    known_words = Column(Integer, nullable=False, default=0)
    problematic_words = Column(Integer, nullable=False, default=0)
    
    dayly_goal = Column(Integer, default=5)
    last_day_learned = Column(Date, nullable=True)
    last_learn_count = Column(Integer, default=0)

class Example(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True, autoincrement=True)
    english = Column(String, nullable=False)
    russian = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
    
    # words = relationship('Word', secondary=word_example_association, back_populates='examples')
    word_id = Column(Integer, ForeignKey("words.id", ondelete='CASCADE'))
    word = relationship("Word", back_populates="examples")
    
    
    def __str__(self):
        return self.english
    
    def __repr__(self):
        return self.english

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    name_translated = Column(String, nullable=True, default=None)
    picture = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=True)
    
    sort_order = Column(Integer, default=0)
    
    words = relationship('Word', secondary=word_category_association, back_populates='categories')
    users = relationship('User', secondary=user_category_association, back_populates='categories')
    
    
    def __str__(self):
        return f"{self.id} - {self.name} - {self.picture} - {self.owner_id}"
    
    def __repr___(self):
        return f"{self.id} - {self.name}"

class Relation_user_word(Base):
    """
    Intervals
        1h
        5h
        1d
        5d
        20d
        2m
    
    States
        0 - not learning (new)
        1 - learning
        2 - learning and problematic
        3 - learned
        4 - already known
    """
    __tablename__ = "user_word_relations"
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True)
    state = Column(Integer, nullable=False, default=False, index=True)
    repeat_iteration = Column(Integer, nullable=False, default=0)
    next_repeat = Column(DateTime, nullable=True)
    
    


# Создание подключения к базе данных
# engine = create_engine('sqlite:///./test.db')
# Base.metadata.create_all(bind=engine)

# Session = sessionmaker(bind=engine)
# session = Session()