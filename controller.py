# from sendlk.engine import SMS
# from sendlk.responses import SmsResponse
# from sendlk.exceptions import SendLKException
# from sendlk.options import SendLKVerifyOption, SendLKCodeTemplet
# from fastapi.exceptions import HTTPException
# from starlette.responses import JSONResponse
# import os
# def send_verify_code(phone_number: str) -> str:

#     try:
#         # Create the SMS option object
#         options: SendLKVerifyOption = SendLKVerifyOption(
#             code_length=4,
#             expires_in=3,
#             sender_id=SENDER_ID,
#             code_templet=CustomCodeTemplet()
#         )

#         response = SMS.send_verify_code(number=phone_number, verify_option=options)
#         token = response.data.get("token", None)
#         return token
#     except SendLKException as e:
#         raise HTTPException(status_code=400, detail=e.message)
