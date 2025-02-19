export const rules = {
  required: (value: any) => !!value || "必須填寫",
  // length limit function
  passwordLength: (value: any) =>
    (value && value.length >= 3 && value.length <= 20) ||
    "密碼長度需介於 3-20 字元",
  englishAndNumber: (value: any) =>
    /^[a-zA-Z0-9]+$/.test(value) || "只能有英文或數字",
  accountLength: (value: any) =>
    (value && value.length >= 3 && value.length <= 20) ||
    "帳號長度需介於 3-20 字元",
  safeProblemLength: (value: any) =>
    (value && value.length <= 30) || "安全問題需介於 30 字以內",
  safeAnswerLength: (value: any) =>
    (value && value.length <= 30) || "安全問題的答案需介於 30 字以內",
  checkPassword: (value: any, password: any) =>
    value === password || "密碼不一致",
};
