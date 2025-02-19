import traceback

from fastapi import (APIRouter, File, Form, Header, HTTPException, Request,
                     UploadFile)
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT
from domain.database.data_model.User import User
from domain.database.database import Session, engine
from domain.validation.InputValidator import InputValidator

router = APIRouter()


class RegisterRequest(BaseModel):
    account: str
    password: str


class LoginRequest(BaseModel):
    account: str
    password: str


# class ForgetPasswordRequest(BaseModel):
#     account: str
#     safe_answer: str


class ResetPasswordRequest(BaseModel):
    account: str
    password: str


class deleteAccountRequest(BaseModel):
    account: str


@router.get("/")
def auth_root():
    return {"msg": "auth"}


@router.post("/register", status_code=201)
def auth_register(request: RegisterRequest, authorization: str = Header(None)):
    if request.account != "admin":
        token = None
        if authorization is not None:
            token = authorization.split(" ")[1]

        jwt_info = JWT.jwt_required(token, need_admin=True)

    if not InputValidator.validate_account(request.account):
        raise HTTPException(status_code=400, detail="帳號不合法")
    if not InputValidator.validate_password(request.password):
        raise HTTPException(status_code=400, detail="密碼不合法")

    # check if account already exists
    with Session() as session:
        user = session.query(User).filter(User.account == request.account).first()
        if user is not None:
            raise HTTPException(status_code=409, detail="帳號已存在")

        session.commit()

    salt, hash_password = Hash.hash(request.password)

    with Session() as session:
        new_user = User(
            account=request.account,
            hashed_password=hash_password,
            salt=salt,
        )
        session.add(new_user)
        session.commit()

    if request.account != "admin":
        admin_log = AdminLog()
        admin_log.add_log(
            f"新增管理員帳號: {request.account}",
            jwt_info,
            "權限",
            LogType.CRITICAL,
        )

    return {}


@router.post("/login", status_code=200)
def auth_login(request: LoginRequest):
    if not InputValidator.validate_account(request.account):
        raise HTTPException(status_code=400, detail="帳號不合法")
    if not InputValidator.validate_password(request.password):
        raise HTTPException(status_code=400, detail="密碼不合法")

    # check if account exists
    with Session() as session:
        user = session.query(User).filter(User.account == request.account).first()
        if user is None:
            raise HTTPException(status_code=404, detail="帳號不存在")

        session.expunge(user)
        session.commit()

    # check if password is correct
    salt = user.salt
    hash_password = user.hashed_password
    b_salt = bytes.fromhex(salt)

    _, hash_input_password = Hash.hash(request.password, b_salt)
    if hash_password != hash_input_password:
        raise HTTPException(status_code=401, detail="密碼錯誤")

    jwt_token = JWT.make_jwt_token(user.account, is_admin="1" if user.is_admin else "0")

    admin_log = AdminLog()
    admin_log.add_log(
        "管理員登入",
        {"account": user.account, "is_admin": user.is_admin},
        "登入",
        LogType.INFO,
    )

    return {"token": jwt_token}


@router.post("/reset_password", status_code=200)
async def reset_password(
    request: ResetPasswordRequest, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    # validate input
    if not InputValidator.validate_account(request.account):
        raise HTTPException(status_code=400, detail="帳號不合法")
    if not InputValidator.validate_password(request.password):
        raise HTTPException(status_code=400, detail="密碼不合法")

    try:
        # check if account exists
        with Session() as session:
            user = session.query(User).filter(User.account == request.account).first()
            if user is None:
                raise HTTPException(status_code=404, detail="帳號不存在")

            session.expunge(user)
            session.commit()

        salt, hash_password = Hash.hash(request.password)

        # update password
        with Session() as session:
            user = session.query(User).filter(User.account == request.account).first()
            user.hashed_password = hash_password
            user.salt = salt
            session.commit()

    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="重置密碼失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"重置 {request.account} 的密碼",
        jwt_info,
        "重置",
        LogType.CRITICAL,
    )

    return {}


@router.get("/accounts", status_code=200)
async def get_accounts(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    accounts = []
    with Session() as session:
        users = session.query(User).all()
        for user in users:
            accounts.append(user.account)

    return {"accounts": accounts}


@router.delete("/{account}", status_code=200)
async def delete_account(account: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    try:
        # check if account is 'admin'
        if account == "admin":
            raise HTTPException(status_code=400, detail="無法刪除 admin 帳號")

        # check if account exists
        with Session() as session:
            user = session.query(User).filter(User.account == account).first()
            if user is None:
                raise HTTPException(status_code=404, detail="帳號不存在")

            session.expunge(user)
            session.commit()

        # delete account
        with Session() as session:
            session.query(User).filter(User.account == account).delete()
            session.commit()

    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="刪除帳號失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除帳號: {account}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}


# @router.post("/forget_password", status_code=200)
# def auth_forget_password(request: ForgetPasswordRequest):
#     if not InputValidator.validate_account(request.account):
#         raise HTTPException(status_code=400, detail="帳號不合法")
#     if not InputValidator.validate_safe_question(request.safe_answer):
#         raise HTTPException(status_code=400, detail="安全答案不合法")

#     # check if account exists
#     with Session() as session:
#         user = session.query(User).filter(User.account == request.account).first()
#         if user is None:
#             raise HTTPException(status_code=404, detail="帳號不存在")

#         session.expunge(user)
#         session.commit()

#     _, hash_input_safe_answer = Hash.hash(request.safe_answer, bytes.fromhex(user.salt))

#     # check if safe question and answer are correct
#     if user.hash_safe_answer != hash_input_safe_answer:
#         raise HTTPException(status_code=401, detail="安全答案錯誤")

#     # generate token
#     jwt_token = JWT.make_jwt_token(user.account, is_admin="1" if user.is_admin else "0")
#     return {"token": jwt_token}
