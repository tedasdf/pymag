from fastapi import FastAPI
from db.main1 import FileModel, FunctionModel , CallModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI()


func_group = [
    FunctionModel(token='search' , parent=('file' , 'test.py'), process=['print("This is the wrong search")']),
    FunctionModel(token='beta' , parent=('file', 'test.py'), process=['print("this still connects")' , CallModel(func_token = 'search', parent=('function' , 'beta')), 'b = Nothing()\nb.beta()' ]),
    FunctionModel(token='alpha' , parent=('file', 'test.py'), process=['re.search("hello world")', CallModel(func_token = 'beta', parent=('function' , 'beta')), 'match()' ])
]
# In-memory storage
files_group = {'test.py': FileModel(token='test', path='test.py' , function_list=func_group,  class_list=[])}



# @app.post("/file")
# async def post_file(source_path: str, file_group: FileModel):
#     # Save file metadata
#     files_group[source_path] = file_group.dict()
#     return {
#         "file path": source_path,
#         "pydantic basemodel": file_group.dict()
#     }

# @app.post("/function")
# async def post_function(source_path:str , func_group: FunctionModel):
#     func_group[source_path] = func_group.dict()
#     return {
#         "file path": source_path,
#         "pydantic basemodel": func_group.dict()
#     }
# Allow all origins (or specify a list of origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, replace with specific URLs if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Sample node dictionary
node_dict = {
    "1": "btiche",
    "2": "node2",
    "3": "node3",
}

# Example endpoint that accepts the FileModel
@app.post("/file")
async def upload_file(file: FileModel):
    # For now, just return the received file data
    files_group[file.token] = file
    return {"received_file": file.dict()}

# Example endpoint that accepts the FileModel
@app.get("/file")
async def get_file():
    # For now, just return the received file data
    
    return [files_group['test.py']]



# @app.get("/file")
# async def get_file(source_path: str):
#     # Return specific file metadata
#     return {"uploaded_files": files_group.get(source_path)}

# @app.get("/file/get_all_files")
# async def get_all_files():
#     # Return all stored metadata
#     return files_group




@app.get('/nodes')
async def get_all_nodes():
    # Return all the nodes in the dictionary
    return node_dict

@app.post('/node')
async def post_node(id, node):
    node_dict[id] = node
    return "succes"