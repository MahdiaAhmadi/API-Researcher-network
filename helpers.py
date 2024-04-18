from bson.objectid import ObjectId


def responseid_handler(response):
    sanitized_resp = {}
    for k,v in response.items():
        if k == "_id":
            sanitized_resp["id"] = str(v)
        elif k == "id":
            pass
        else:
            sanitized_resp[k] = v

    return sanitized_resp

def listresponse_handler(responselist):
    sanitizedList = []
    for item in responselist:
        sanitizedList.append(responseid_handler(item))
    return sanitizedList

# Generic CRUD methods for all collections
# TODO : add types to all methods
async def getAll(collection):
    items = []
    async for item in collection.find():
        items.append(responseid_handler(item))
    return items



async def getOne(collection, id):
    item = await collection.find_one({"_id": ObjectId(id)})
    if item:
        return responseid_handler(item)

async def addOne(collection, data):
    item = await collection.insert_one(data)
    new_item = await collection.find_one({"_id": item.inserted_id})
    return responseid_handler(new_item)

async def updateOne(collection, id, data):
    if len(data) < 1:
        return False
    item = await collection.find_one({ "_id": ObjectId(id) })
    if item:
        updated_item = await collection.update_one(
            { "_id": ObjectId(id) }, { "$set": data }
        )
        if updated_item:
            return True
        return False

async def deleteOne(collection, id):
    item = await collection.find_one({ "_id": ObjectId(id) })
    if item:
        await collection.delete_one({"_id": ObjectId(id)})
        return True


def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
