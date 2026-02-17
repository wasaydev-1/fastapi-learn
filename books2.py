from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


class Book():
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int


    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create")   
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)


    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "A new book",
                    "author": "An author",
                    "description": "A description",
                    "rating": 5,
                    "published_date": 2008
                }
            ]
        }
    }


BOOKS = [
   Book(1, "Atomic Habits", "James Clear", "A practical guide to building good habits and breaking bad ones.", 5, 2018),
   Book(2, "The Alchemist", "Paulo Coelho", "A philosophical novel about a shepherd's journey to find treasure and purpose.", 4, 2008 ),
   Book(3, "Clean Code", "Robert C. Martin", "A handbook of agile software craftsmanship and writing maintainable code.", 5, 2008),
   Book(4, "Deep Work", "Cal Newport", "Rules for focused success in a distracted world.", 4, 2016),
   Book(5, "1984", "George Orwell", "A dystopian novel exploring totalitarianism, surveillance, and loss of freedom.", 5, 2001),
]


@app.get("/books")
async def get_books():
    return BOOKS


@app.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    

@app.get("/books/")
async def get_book_by_rating(rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/published/")
async def get_book_by_published_date(published_date: int):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())    
    BOOKS.append(find_book_id(new_book))
    return new_book


def find_book_id(book: Book):
    # if len(BOOKS) > 0:
    #     book.id=BOOKS[-1].id+1
    # else:
    #     book.id=1
    # return book
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.put("/books/update-book")
async def update_book(book_request: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = book_request
            return BOOKS[i]
   

@app.delete("/books/delete-book")
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            return {"message": "Book deleted successfully"}
    return {"message": "Book not found"}
