class InputValidator:
    def __init__(self):
        pass

    def _length_limit(input, min_length, max_length):
        if len(input) < min_length or len(input) > max_length:
            return False
        return True

    def _english_and_number_only(input):
        return input.isalnum()

    def validate_account(account):
        if account is None:
            return False
        if not InputValidator._length_limit(account, 3, 20):
            return False
        if not InputValidator._english_and_number_only(account):
            return False

        return True

    def validate_password(password):
        if password is None:
            return False
        if not InputValidator._length_limit(password, 3, 20):
            return False
        if not InputValidator._english_and_number_only(password):
            return False

        return True

    def validate_safe_question(safe_question):
        if safe_question is None:
            return False
        if not InputValidator._length_limit(safe_question, 1, 30):
            return False

        return True

    def validate_safe_answer(safe_answer):
        if safe_answer is None:
            return False
        if not InputValidator._length_limit(safe_answer, 1, 30):
            return False

        return True
