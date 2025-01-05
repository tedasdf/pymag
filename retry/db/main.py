# from typing import Dict, List, Union
# from pydantic import BaseModel, Field


# # Forward declare the class references to avoid circular dependency
# class FunctionModel(BaseModel):
#     token: str
#     process: List[Union['CallModel', 'VariableModel', str]] = Field(default_factory=list)  # References to Call and Variable (forward declaration)
#     parent: Union['ClassModel', 'FileModel', None] = None # Reference to ClassModel and FileModel


# class CallModel(BaseModel):
#     func: Union[FunctionModel, None] = None


# class VariableModel(BaseModel):
#     points_to: Union[CallModel, 'ClassModel', None] = None  # `points_to` can be either Call or ClassModel
#     token: str


# class LogicStatModel(BaseModel):
#     cond_type: str
#     process: List[Union[CallModel, VariableModel, str]]  # Can contain Call, Variable, or str


# class ClassModel(BaseModel):
#     functions: List['FunctionModel'] = Field(default_factory=list)  
#     token: str


# class FileModel(BaseModel):
#     token: str
#     path: str
#     function_dict: Dict[str, 'FunctionModel'] = Field(default_factory=dict)  # Use forward reference
#     class_list: Dict[str, 'ClassModel'] = Field(default_factory=dict)


# # Resolve forward references
# FileModel.update_forward_refs()
# FunctionModel.update_forward_refs()
# CallModel.update_forward_refs()
# VariableModel.update_forward_refs()
# ClassModel.update_forward_refs()