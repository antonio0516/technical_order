from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.database.database import Session, engine
from domain.validation.InputValidator import InputValidator

router = APIRouter()


# class GetSafeQuestionResponse(BaseModel):
#     safe_question: str


# class ResetPasswordRequest(BaseModel):
#     new_password: str
#     token: str


# @router.get("/{account}/safe_question", status_code=200)
# def get_safe_question(account: str):
#     if not InputValidator.validate_account(account):
#         raise HTTPException(status_code=400, detail="帳號不合法")
#     # check if account exists
#     with Session() as session:
#         user = session.query(User).filter(User.account == account).first()
#         if user is None:
#             raise HTTPException(status_code=404, detail="帳號不存在")

#         session.expunge(user)
#         session.commit()

#     return {"safe_question": user.safe_question}


# @router.patch("/{account}/password", status_code=200)
# @JWT.jwt_required()
# async def reset_password(request: ResetPasswordRequest, jwt_info={}):
#     if not InputValidator.validate_password(request.new_password):
#         raise HTTPException(status_code=400, detail="密碼不合法")

#     account = jwt_info["account"]
#     # check if token's account exists
#     with Session() as session:
#         user = session.query(User).filter(User.account == account).first()
#         if user is None:
#             raise HTTPException(status_code=404, detail="用戶不存在")

#         session.expunge(user)
#         session.commit()

#     salt, hash_password = Hash.hash(request.new_password)

#     with Session() as session:
#         user = session.query(User).filter(User.account == account).first()
#         user.hashed_password = hash_password
#         user.salt = salt
#         session.commit()

#     return {}
