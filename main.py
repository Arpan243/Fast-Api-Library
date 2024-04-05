from fastapi import FastAPI, Query, Path, HTTPException, Response
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb+srv://arpan:Asdfg!234@tutorial1.35o0lex.mongodb.net/")
db = client["Library"]
students_collection = db["students"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

@app.post("/students", status_code=201)
async def create_student(student: Student):
    student_dict = student.dict()
    result = students_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

@app.get("/students", response_model=dict)
async def list_students(country: str = Query(None), age: int = Query(None)):
    filter_query = {}
    if country:
        filter_query["address.country"] = country
    if age is not None:
        filter_query["age"] = {"$gte": age}
    
    filtered_students = students_collection.find(filter_query, {"_id": 0, "name": 1, "age": 1})
    return {"data": list(filtered_students)}

@app.get("/students/{id}", response_model=Student)
async def get_student(id: str = Path(...)):
    student = students_collection.find_one({"_id": ObjectId(id)})
    if student:
        student['_id'] = str(student['_id'])
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}")
async def update_student(student: Student, id: str = Path(...)):
    student_dict = student.dict()
    result = students_collection.update_one({"_id": ObjectId(id)}, {"$set": student_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return Response(status_code=204)

@app.delete("/students/{id}")
async def delete_student(id: str = Path(...)):
    result = students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
