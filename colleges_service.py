import motor.motor_asyncio
from bson.objectid import ObjectId
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from models import Institution, UpdateInstitutionModel

MONGO_DETAILS = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.research_network

college_collection = database.get_collection("colleges")

# helper
def college_helper(college):
    return {
        "id": str(college["_id"]),
        "name": college["name"],
        "homepage": college["homepage"],
    }

def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}

# Retrieve all colleges present in the database
async def retrieve_colleges():
    colleges = []
    async for college in college_collection.find():
        colleges.append(college_helper(college))
    return colleges


# Add a new college into to the database
async def add_college(college_data: dict) -> dict:
    college = await college_collection.insert_one(college_data)
    new_college = await college_collection.find_one({"_id": college.inserted_id})
    return college_helper(new_college)


# Retrieve a college with a matching ID
async def retrieve_college(id: str) -> dict:
    college = await college_collection.find_one({"_id": ObjectId(id)})
    if college:
        return college_helper(college)


# Update a college with a matching ID
async def update_college(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    college = await college_collection.find_one({"_id": ObjectId(id)})
    if college:
        updated_college = await college_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_college:
            return True
        return False


# Delete a college from the database
async def delete_college(id: str):
    college = await college_collection.find_one({"_id": ObjectId(id)})
    if college:
        await college_collection.delete_one({"_id": ObjectId(id)})
        return True

CollegeRouter = APIRouter()
@CollegeRouter.post("/", response_description="College added to database")
async def add_college_data(college: Institution = Body(...)):
    college = jsonable_encoder(college)
    new_college = await add_college(college)
    return ResponseModel(new_college, "College added successfully.")

@CollegeRouter.get("/", response_description="College retrieved")
async def get_colleges():
    colleges = await retrieve_colleges()
    if colleges:
        return ResponseModel(colleges, "Colleges data retrieved successfully")
    return ResponseModel(colleges, "Empty list returned")

@CollegeRouter.get("/{id}", response_description="College data retrieved")
async def get_college_data(id):
    college = await retrieve_college(id)
    if college:
        return ResponseModel(college, "College data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "College doesn't exist.")

@CollegeRouter.put("/{id}")
async def update_college_data(id: str, req: UpdateInstitutionModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_college = await update_college(id, req)
    if updated_college:
        return ResponseModel(
            "College with ID: {} name update is successful".format(id),
            "College name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the college data.",
    )

@CollegeRouter.delete("/{id}", response_description="College data deleted from the database")
async def delete_college_data(id: str):
    deleted_college = await delete_college(id)
    if deleted_college:
        return ResponseModel(
            "College with ID: {} removed".format(id), "College deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "College with id {0} doesn't exist".format(id)
    )

