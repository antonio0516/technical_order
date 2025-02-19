import time
from enum import Enum
from functools import wraps

import jwt
from fastapi import HTTPException, Request

from domain.get_config import Config


class JWTDecodeError(Enum):
    DECODE_ERROR = 0
    EXPIRED = 1
    PERMISSION_DENIED = 2


class JWT:
    def jwt_required(token, need_admin):
        if token is None:
            raise HTTPException(status_code=401, detail="無法取得 Token")

        jwt_info = JWT.check_jwt_token_and_get_info(token, check_is_admin=need_admin)
        if not jwt_info["success"]:
            if jwt_info["error_event"] == JWTDecodeError.DECODE_ERROR:
                raise HTTPException(status_code=401, detail="Token 解析錯誤")
            elif jwt_info["error_event"] == JWTDecodeError.EXPIRED:
                raise HTTPException(status_code=401, detail="Token 已過期")
            elif jwt_info["error_event"] == JWTDecodeError.PERMISSION_DENIED:
                raise HTTPException(status_code=401, detail="Token 權限不足")
            else:
                raise HTTPException(status_code=401, detail="Token 不合法")

        return jwt_info["info"]

    def make_jwt_token(account: str, is_admin="0") -> str:
        CONFIG = Config.get_config()
        return jwt.encode(
            {
                "account": account,
                "isAdmin": is_admin,
                "exp": time.time() + 60 * 60 * CONFIG.jwt["exp"],
            },
            CONFIG.jwt["secret_key"],
            algorithm="HS256",
        )

    def check_jwt_token_and_get_info(token: str, check_is_admin):
        return_info = {
            "success": False,
            "error_event": None,
            "info": {},
        }

        CONFIG = Config.get_config()

        """
        Check token integrity
        """
        try:
            info = jwt.decode(
                token,
                CONFIG.jwt["secret_key"],
                algorithms=["HS256"],
            )
        except:
            return_info["error_event"] = JWTDecodeError.DECODE_ERROR
            return return_info

        """
        Check token timeliness
        """
        if time.time() > info["exp"]:
            return_info["error_event"] = JWTDecodeError.EXPIRED
            return return_info

        if check_is_admin:
            """
            Check token authority
            """
            if info["isAdmin"] != "1":
                return_info["error_event"] = JWTDecodeError.PERMISSION_DENIED
                return return_info

        return_info["success"] = True
        return_info["info"] = info
        return return_info
