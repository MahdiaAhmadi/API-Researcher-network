import motor.motor_asyncio
from bson.objectid import ObjectId
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from helpers import (ErrorResponseModel, ResponseModel, addOne, deleteOne,
                     getAll, getOne, updateOne)
from models import Institution, UpdateInstitutionModel

MONGO_DETAILS = "mongodb+srv://felipebuenosouza:as%40ClusterAcess@cluster0.a5kds6l.mongodb.net/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.research_network
institution_collection = database.get_collection("colleges")

InstitutionRouter = APIRouter()
@InstitutionRouter.post("/", response_description="Institution added to database")
async def add_institution_data(institution: Institution = Body(...)):
    institution = jsonable_encoder(institution)
    new_institution = await addOne(institution_collection, institution)
    return ResponseModel(new_institution, "Institution added successfully.")

@InstitutionRouter.get("/", response_description="Institution retrieved")
async def get_institutions():
    institutions = await getAll(institution_collection)
    if institutions:
        return ResponseModel(institutions, "Institutions data retrieved successfully")
    return ResponseModel(institutions, "Empty list returned")

@InstitutionRouter.get("/{id}", response_description="Institution data retrieved")
async def get_institution_data(id):
    institution = await getOne(institution_collection, id)
    if institution:
        return ResponseModel(institution, "Institution data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "Institution doesn't exist.")

@InstitutionRouter.put("/{id}")
async def update_institution_data(id: str, req: UpdateInstitutionModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_institution = await updateOne(institution_collection, id, req)
    if updated_institution:
        return ResponseModel(
            "Institution with ID: {} name update is successful".format(id),
            "Institution name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the institution data.",
    )

@InstitutionRouter.delete("/{id}", response_description="Institution data deleted from the database")
async def delete_institution_data(id: str):
    deleted_institution = await deleteOne(institution_collection, id)
    if deleted_institution:
        return ResponseModel(
            "Institution with ID: {} removed".format(id), "Institution deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "Institution with id {0} doesn't exist".format(id)
    )

