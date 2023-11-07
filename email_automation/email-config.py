import boto3
from botocore.exceptions import ClientError
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def email_extract():
    with open ('/AWS-test-ebike.nrel-op.json') as config_file:
        data = json.load(config_file)
        intro = data['intro']
        emails = [i.strip() for i in intro['admin_users'].split(",")]
    return emails

print(email_extract())

filename = "ebikethere-garfield-county"
pool_name = "nrelopenpath-prod-" + filename
pool_id = []
AWS_REGION = "us-west-2" 


# def get_userpool_name():
client = boto3.client(
'cognito-idp',
aws_access_key_id="",
aws_secret_access_key= "",
aws_session_token="", 
region_name=AWS_REGION
)
response = client.list_user_pools(MaxResults=60)
UserPoolExist = False

for i in response["UserPools"]:
    if i["Name"] == pool_name:
        pool_id.append(i["Id"])
        UserPoolExist = True
    else:
        print("Pool DNE! Looking...")
        continue

if UserPoolExist:
    print(pool_name + " pool exists! Adding users...")

#we can create the pool automatically if it does not exist. 
if not UserPoolExist:
    print(pool_name + " does not exist! Creating pool...")
#     response = client.create_user_pool(
#     PoolName=pool_name,
#     Policies={
#         'PasswordPolicy': {
#             'MinimumLength': 123,
#             'RequireUppercase': True|False,
#             'RequireLowercase': True|False,
#             'RequireNumbers': True|False,
#             'RequireSymbols': True|False,
#             'TemporaryPasswordValidityDays': 123
#         }
#     },
#     DeletionProtection='ACTIVE'|'INACTIVE',
#     LambdaConfig={
#         'PreSignUp': 'string',
#         'CustomMessage': 'string',
#         'PostConfirmation': 'string',
#         'PreAuthentication': 'string',
#         'PostAuthentication': 'string',
#         'DefineAuthChallenge': 'string',
#         'CreateAuthChallenge': 'string',
#         'VerifyAuthChallengeResponse': 'string',
#         'PreTokenGeneration': 'string',
#         'UserMigration': 'string',
#         'CustomSMSSender': {
#             'LambdaVersion': 'V1_0',
#             'LambdaArn': 'string'
#         },
#         'CustomEmailSender': {
#             'LambdaVersion': 'V1_0',
#             'LambdaArn': 'string'
#         },
#         'KMSKeyID': 'string'
#     },
#     AutoVerifiedAttributes=[
#         'phone_number'|'email',
#     ],
#     AliasAttributes=[
#         'phone_number'|'email'|'preferred_username',
#     ],
#     UsernameAttributes=[
#         'phone_number'|'email',
#     ],
#     SmsVerificationMessage='string',
#     EmailVerificationMessage='string',
#     EmailVerificationSubject='string',
#     VerificationMessageTemplate={
#         'SmsMessage': 'string',
#         'EmailMessage': 'string',
#         'EmailSubject': 'string',
#         'EmailMessageByLink': 'string',
#         'EmailSubjectByLink': 'string',
#         'DefaultEmailOption': 'CONFIRM_WITH_LINK'|'CONFIRM_WITH_CODE'
#     },
#     SmsAuthenticationMessage='string',
#     MfaConfiguration='OFF'|'ON'|'OPTIONAL',
#     UserAttributeUpdateSettings={
#         'AttributesRequireVerificationBeforeUpdate': [
#             'phone_number'|'email',
#         ]
#     },
#     DeviceConfiguration={
#         'ChallengeRequiredOnNewDevice': True|False,
#         'DeviceOnlyRememberedOnUserPrompt': True|False
#     },
#     EmailConfiguration={
#         'SourceArn': 'string',
#         'ReplyToEmailAddress': 'string',
#         'EmailSendingAccount': 'COGNITO_DEFAULT'|'DEVELOPER',
#         'From': 'string',
#         'ConfigurationSet': 'string'
#     },
#     SmsConfiguration={
#         'SnsCallerArn': 'string',
#         'ExternalId': 'string',
#         'SnsRegion': 'string'
#     },
#     UserPoolTags={
#         'string': 'string'
#     },
#     AdminCreateUserConfig={
#         'AllowAdminCreateUserOnly': True|False,
#         'UnusedAccountValidityDays': 123,
#         'InviteMessageTemplate': {
#             'SMSMessage': 'string',
#             'EmailMessage': 'string',
#             'EmailSubject': 'string'
#         }
#     },
#     Schema=[
#         {
#             'Name': 'string',
#             'AttributeDataType': 'String'|'Number'|'DateTime'|'Boolean',
#             'DeveloperOnlyAttribute': True|False,
#             'Mutable': True|False,
#             'Required': True|False,
#             'NumberAttributeConstraints': {
#                 'MinValue': 'string',
#                 'MaxValue': 'string'
#             },
#             'StringAttributeConstraints': {
#                 'MinLength': 'string',
#                 'MaxLength': 'string'
#             }
#         },
#     ],
#     UserPoolAddOns={
#         'AdvancedSecurityMode': 'OFF'|'AUDIT'|'ENFORCED'
#     },
#     UsernameConfiguration={
#         'CaseSensitive': True|False
#     },
#     AccountRecoverySetting={
#         'RecoveryMechanisms': [
#             {
#                 'Priority': 123,
#                 'Name': 'verified_email'|'verified_phone_number'|'admin_only'
#             },
#         ]
#     }
# )

def user_already_exists(pool_id, email):
    try:
        response = client.list_users(UserPoolId=pool_id)
        users = response["Users"]
        result = False
        for i in users:
            for k, v in i.items():
                if k == "Attributes":
                    for j in v:
                        if j["Name"] == "email":
                            user_email = str(j["Value"])
                            # print(user_email)
                            if str(email) == user_email:
                                result = True
        # print(result)
        return result
    except ClientError as err:
        logger.error(
            "Couldn't list users for %s. Here's why: %s: %s",
            pool_id,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

for email in email_extract():
    if not user_already_exists(pool_id[0], email):
        print(email + " not in user pool! Creating account...")
        response = client.admin_create_user(
            #extra info on these params here: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_create_user.html
            UserPoolId=pool_id[0],
            #If user pool only supports phone numbers or email addresses as sign-in attributes, Amazon Cognito automatically generates a username value.
            Username='string',
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email,
                },
            ],
            #The temporary password is valid only once.
            #If you don’t specify a value, Amazon Cognito generates a temp password for you.
            TemporaryPassword='string', 
            ForceAliasCreation=True,
            MessageAction='RESEND',
            DesiredDeliveryMediums=[
                'EMAIL',
            ],
            ClientMetadata={
                'string': 'string'
            }
        )



#     

# ses = boto3.client(
#     'ses',
#     aws_access_key_id="",
#     aws_secret_access_key= "",
#     aws_session_token="")

# response = ses.verify_domain_identity(Domain = 'openpath@nrel.gov')

# print(response)

# # Replace sender@example.com with your "From" address.
# # This address must be verified with Amazon SES.
# SENDER = "OpenPATH  <openpath@nrel.gov>"

# # Replace recipient@example.com with a "To" address. If your account 
# # is still in the sandbox, this address must be verified.
# RECIPIENT = email_extract()

# # Specify a configuration set. If you do not want to use a configuration
# # set, comment the following variable, and the 
# # ConfigurationSetName=CONFIGURATION_SET argument below.
# # CONFIGURATION_SET = "ConfigSet"

# # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
# AWS_REGION = "us-west-2"

# # The subject line for the email.
# SUBJECT = "OpenPATH Admin Account Registration"

# # The email body for recipients with non-HTML email clients.
# BODY_TEXT = ("Amazon SES Test (Python)\r\n"
#              "This email was sent with Amazon SES using the "
#              "AWS SDK for Python (Boto). *******"
#             )
            
# # The HTML body of the email.
# BODY_HTML = """<html>
# <head></head>
# <body>
# #   <h1>Amazon SES Test (SDK for Python)</h1>
# #   <p>This email was sent with
# #     <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
# #     <a href='https://aws.amazon.com/sdk-for-python/'>
# #       AWS SDK for Python (Boto)</a>.</p>
# # </body>
# # </html>
# #             """            

# # The character encoding for the email.
# CHARSET = "UTF-8"

# # Create a new SES resource and specify a region.
# client = boto3.client(
#     'ses',
#     aws_access_key_id="ASIA6NVCXDIRNULC5CHP",
#     aws_secret_access_key= "wRAWvN1Hm1MVRoCv4xShRyPcJeOPiUd5STPIk4Hh",
#     aws_session_token="IQoJb3JpZ2luX2VjEA0aCXVzLXdlc3QtMiJGMEQCICRyAqyFyD/IcS5LsVbNi0S/saWE/kV99IynK19BJKC1AiAOTy3Lnk82KAVJK0F39fxtA/znswj7MLMC5fj1ehohKSq3BAg2EAAaDDk5MTQwNDk1NjE5NCIMoyon7TW5z0cxPaouKpQEIcgkDd3XmM82ZMNLZaUAwwMNiu2a6Ckzc7U2oHAp3Au3fUmqAOPzKhROPccNChe0Istybcsvetj49lK8+11Bte56EgmUmrDmh2a4nPNDaoRQr5t1KmXTp3P0UIvzHUAVtp6dl5uEw2bCtfv4ReNUgmP3Ef0Mh6RzQPjauJSK+41rwgcr7e9kRJGL3o3DS8F1fNvCJQL9PwnuVdlqqrN1CVcm+eLGOVSblsyKYekmSfqJM743Hj+syNThEP+z81/43OaLjqhrnycGQPYxh6klkkMVJBplpdb/Iq22YLls6yB25/MukGq45cFFm8pBaeeJlYNkdp2m6G7/zk9Jp3Txa0bnZS0f4+BJk4mtlg0zth7hxtsyJx0E9j4bwrlTygOzGY2MJqLnwEEW4vWTbPjrss7ABbmeFtEW2CMZGEqCZpE38l9usDpRXE7ENvWFlYTy+tJ8VoYvUMnM/+Ft0smjq2KXKSNm7oDGVFUhMUz8rbTxjVZSGHqZhUuWDoJ+xdOwH6Xsg17QUho0gNFw0+So1x5wy7mofTYulNpAz5GVaxD45kH1WaFXXMsr1NPZopceuzpN6h0bnwwSSMzGWykKq/gVsDu1vLYlKqKE3oXB+Pw+XNBlH19OCW5BHXt+b6WcaUOTAqBNO6h8Ml0KFZh7BhJM04MtzShwCmo4rWXBxvitLxGCAT2jREODE2QmrByk8fC7VzCtrdupBjqnAVB+F2BFe0Ufrd7lsLB3BO8lp42oH8eXkLqlrMAiISYBbTqVPJliCqcTOsYIaWcXWBP0BMSOHclkMrncASAMTYwmRbjHAJohCToRMUZIiVXHWCxquut4Cf/QBtZpg/I16wt9LebJy5TivIxsNoMMnqkgbsvOCxdAK5Nd8XXszFHrDkQWR24/BLLI3WnOi1jWTHJ4TS1O8VYIGCgomGg4ewvqWYRS5fZn",
#     region_name=AWS_REGION
#     )

# # Try to send the email.
# try:
#     #Provide the contents of the email.
#     response = client.send_email(
#         Destination={
#             'ToAddresses': [
#                 RECIPIENT,
#             ],
#         },
#         Message={
#             'Body': {
#                 'Html': {
#                     'Charset': CHARSET,
#                     'Data': BODY_HTML,
#                 },
#                 'Text': {
#                     'Charset': CHARSET,
#                     'Data': BODY_TEXT,
#                 },
#             },
#             'Subject': {
#                 'Charset': CHARSET,
#                 'Data': SUBJECT,
#             },
#         },
#         Source=SENDER,
#         # If you are not using a configuration set, comment or delete the
#         # following line
#         # ConfigurationSetName=CONFIGURATION_SET,
#     )
# # Display an error if something goes wrong.	
# except ClientError as e:
#     print(e.response['Error']['Message'])
# else:
#     print("Email sent! Message ID:"),
#     print(response['MessageId'])