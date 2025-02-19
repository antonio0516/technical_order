from domain.auth.Hash import Hash
from domain.database.data_model.User import User
from domain.database.database import Session
from domain.validation.InputValidator import InputValidator

if __name__ == "__main__":
    # input account, password, safe_question, safe_answer from terminal
    account = input("account: ")
    password = input("password: ")
    safe_question = ""
    safe_answer = ""

    if not InputValidator.validate_account(account):
        print("帳號不合法")
        raise SystemExit
    if not InputValidator.validate_password(password):
        print("密碼不合法")
        raise SystemExit

    # check if account already exists
    with Session() as session:
        user = session.query(User).filter(User.account == account).first()
        if user is not None:
            print("帳號已存在")
            raise SystemExit

        session.commit()

    salt, hash_password = Hash.hash(password)
    b_salt = bytes.fromhex(salt)
    _, hash_safe_answer = Hash.hash(safe_answer, b_salt)

    with Session() as session:
        new_user = User(
            account=account,
            hashed_password=hash_password,
            salt=salt,
            safe_question="",
            hash_safe_answer="",
            is_admin=True,
        )
        session.add(new_user)
        session.commit()

    print("帳號建立成功")
