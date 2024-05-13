from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import datetime

app = FastAPI()

engine = create_engine('postgresql://postgres:root@localhost:5432/postgres')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)
    post = relationship('Post')


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True) 
    text = Column(String)
    created = Column(DateTime) 
    authorid = Column(
        Integer, ForeignKey('author.id', ondelete='CASCADE'))
    author =  relationship('Author')
    subtitle = Column(String)


Base.metadata.create_all(bind=engine)


@app.post("/authors")
def create_author(name: str, age: int):
    author = Author(name=name,  age=age)
    session.add(author)
    session.commit()

    return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age})

@app.put("/authors")
def put_author(id: str, name: str, age: int):
    author = session.query(Author).filter_by(id=id).first()
    content_reponse = {}
    status_code = 200   

    if author is not None:
        author.name = name
        author.age = age
        session.commit()
        content_reponse = {'id': author.id, 'name': author.name, 'age': author.age}

        
    else:
        content_reponse = {'message': 'Author not found'} 
        status_code=404
    
    return JSONResponse(content=content_reponse, status_code=status_code)

@app.get("/authors")
def read_authors():
    authors = session.query(Author).all()

    authors_list = []

    for author in authors:
        authors_dict = {'id': author.id, 'name': author.name, 'age': author.age}
        authors_list.append(authors_dict)

    return JSONResponse(content=authors_list)

@app.post("/posts")
def create_posts(text: str, author_id: str, subtitle: str):
    author = session.query(Author).filter_by(id=author_id).first()
    post = Post(text=text, authorid=author_id, author=author, created=datetime.datetime.now(), subtitle=subtitle)
    session.add(post)
    session.commit()

    return JSONResponse(content={'id': post.id, 'text': post.text, 'created': str(post.created), 'authorid': post.authorid, 'subtitle': post.subtitle})

@app.put("/posts")
def put_posts(id: str, text: str, subtitle: str):
    posts = session.query(Post).filter_by(id=id).first()
    posts.text = text
    posts.subtitle = subtitle
    session.commit()

    return JSONResponse(content={'id': posts.id, 'text': posts.text, 'created': str(posts.created), 'authorid': posts.authorid, 'subtitle': posts.subtitle})

@app.get("/posts")
def read_posts():
    posts = session.query(Post).all()

    posts_list = []

    for post in posts:
        posts_dict = {'id': post.id, 'text': post.text, 'created': str(post.created), 'authorid': post.authorid, 'subtitle': post.subtitle}
        posts_list.append(posts_dict)

    return JSONResponse(content=posts_list)

@app.get("/authorAndPosts")
def posts_and_author():
    query = session.query(Author).join(Post).all()

    list = []

    for item in query:
        posts = []
        for post in item.post:
            posts.append({'id': post.id, 'text': post.text, 'created': str(post.created), 'authorid': post.authorid, 'subtitle': post.subtitle})
        dict = {'id': item.id, 'name': item.name, 'age': item.age, 'post': posts}
        list.append(dict)

    return JSONResponse(content=list)
