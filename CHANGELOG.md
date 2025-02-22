
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.11.3] - 2022-10-17
- Updated google token endpoint.

## [0.11.2] - 2022-10-14
### Changes:
- Removed default `default_max_age` from session claim base classes
- Added a 5 minute `default_max_age` to UserRoleClaim, PermissionClaim and EmailVerificationClaim
- Fix Repetition of root_path in supertokens mididdlware for fastapi [#230](https://github.com/supertokens/supertokens-python/issues/230)

## [0.11.1] - 2022-09-28
### Changes:
- Email verification endpoints will now clear the session if called by a deleted/unknown user

### Additions:
- Adds dashboard recipe
- Added a `username` field to the `SMTPSettings` model for passing custom SMTP server username.

## [0.11.0] - 2022-09-14

### Changes

- Made the `email` parameter optional in `unverify_email`, `revoke_email_verification_tokens`, `is_email_verified`, `verify_email_using_token`, `create_email_verification_token` of the `EmailVerification` recipe.

### Added

- Support for FDI 1.15
- Added support for session claims with related interfaces and classes.
- Added `on_invalid_claim` optional error handler to send InvalidClaim error responses.
- Added `INVALID_CLAIMS` (`InvalidClaimError`) to `SessionErrors`.
- Added `invalid_claim_status_code` optional config to set the status code of InvalidClaim errors.
- Added `override_global_claim_validators` as param of `get_session` and `verify_session`.
- Added `merge_into_access_token_payload` to the Session recipe and session objects which should be preferred to the now deprecated `update_access_token_payload`.
- Added `EmailVerificationClaim`, `UserRoleClaim` and `PermissionClaim`. These claims are now added to the access token payload by default by their respective recipes.
- Added `assert_claims`, `validate_claims_for_session_handle`, `validate_claims_in_jwt_payload` to the Session recipe to support validation of the newly added claims.
- Added `fetch_and_set_claim`, `get_claim_value`, `set_claim_value` and `remove_claim` to the Session recipe to manage claims.
- Added `assert_claims`, `fetch_and_set_claim`, `get_claim_value`, `set_claim_value` and `remove_claim` to session objects to manage claims.
- Added session to the input of `generate_email_verify_token_post`, `verify_email_post`, `is_email_verified_get`.
- Adds default userContext for verifySession calls that contains the request object.

### Breaking Changes
- Removes support for FDI <= 1.14
-   Changed `sign_in_up` third party recipe function to accept just the email as `str` (removed `email_verified: bool`).
-   The frontend SDK should be updated to a version supporting session claims!
    -   supertokens-auth-react: >= 0.25.0
    -   supertokens-web-js: >= 0.2.0
-   `EmailVerification` recipe is now not initialized as part of auth recipes, it should be added to the `recipe_list` directly instead using `emailverification.init()`.
-   Email verification related overrides (`email_verification_feature` attr of `override`) moved from auth recipes into the `EmailVerification` recipe config.
-   Email verification related configs (`email_verification_feature` attr) moved from auth recipes into the `EmailVerification` config object root.
-   ThirdParty recipe no longer takes `email_delivery` config. use `emailverification` recipe's `email_delivery` instead.
-   Moved email verification related configs from the `email_delivery` config of auth recipes into a separate `EmailVerification` email delivery config.
-   Updated return type of `get_email_for_user_id` in the `EmailVerification` recipe config. It should now return an object with status.
-   Removed `get_reset_password_url`, `get_email_verification_url`, `get_link_domain_and_path`. Changing these urls can be done in the email delivery configs instead.
-   Removed `unverify_email`, `revoke_email_verification_tokens`, `is_email_verified`, `verify_email_using_token` and `create_email_verification_token` from auth recipes. These should be called on the `EmailVerification` recipe instead.
-   Changed function signature for email verification APIs to accept a session as an input.
-   Changed Session API interface functions:
    - `refresh_post` now returns a Session container object.
    - `sign_out_post` now takes in an optional session object as a parameter.

### Migration
Before:
```python
from supertokens_python import init, SupertokensConfig, InputAppInfo
from supertokens_python.recipe import emailpassword
from supertokens_python.recipe.emailverification.utils import OverrideConfig

init(
    supertokens_config=SupertokensConfig("..."),
    app_info=InputAppInfo("..."),
    framework="...",
    recipe_list=[
        emailpassword.init(
            # these options should be moved into the EmailVerification config:
            email_verification_feature=emailpassword.InputEmailVerificationConfig("..."),
            override=emailpassword.InputOverrideConfig(
                email_verification_feature=OverrideConfig(
                    # these overrides should be moved into the EmailVerification overrides
                    "..."
                )
            ),
        ),
    ],
)
```

After the update:

```python
from supertokens_python import init, SupertokensConfig, InputAppInfo
from supertokens_python.recipe import emailpassword, emailverification

init(
    supertokens_config=SupertokensConfig("..."),
    app_info=InputAppInfo("..."),
    framework="...",
    recipe_list=[
        emailverification.init(
            "...", # EmailVerification config
            override=emailverification.OverrideConfig(
                # overrides
                "..."
            ),
        ),
        emailpassword.init(),
    ],
)
```

#### Passwordless users and email verification

If you turn on email verification your email-based passwordless users may be redirected to an email verification screen in their existing session.
Logging out and logging in again will solve this problem or they could click the link in the email to verify themselves.

You can avoid this by running a script that will:

1. list all users of passwordless
2. create an emailverification token for each of them if they have email addresses
3. user the token to verify their address

Something similar to this script:

```python
from supertokens_python import init, SupertokensConfig, InputAppInfo
from supertokens_python.recipe import passwordless, emailverification, session
from supertokens_python.recipe.passwordless import ContactEmailOrPhoneConfig


from supertokens_python.syncio import get_users_newest_first
from supertokens_python.recipe.emailverification.syncio import create_email_verification_token, verify_email_using_token
from supertokens_python.recipe.emailverification.interfaces import CreateEmailVerificationTokenOkResult

init(
    supertokens_config=SupertokensConfig("http://localhost:3567"),
    app_info=InputAppInfo(
        app_name="SuperTokens Demo",
        api_domain="https://api.supertokens.io",
        website_domain="supertokens.io",
    ),
    framework="fastapi",
    recipe_list=[
        emailverification.init("REQUIRED"),
        passwordless.init(
            contact_config=ContactEmailOrPhoneConfig(),
            flow_type="USER_INPUT_CODE_AND_MAGIC_LINK",
        ),
        session.init(),
    ],
)

def verify_email_for_passwordless_users():
    pagination_token = None
    done = False
    
    while not done:
        res = get_users_newest_first(
            limit=100,
            pagination_token=pagination_token,
            include_recipe_ids=["passwordless"]
        )

        for user in res.users:
            if user.email is not None:
                token_res = create_email_verification_token(user.user_id, user.email)
                if isinstance(token_res, CreateEmailVerificationTokenOkResult):
                    verify_email_using_token(token_res.token)
        
        done = res.next_pagination_token is None
        if not done:
            pagination_token = res.next_pagination_token

verify_email_for_passwordless_users()
```

#### User roles

The `UserRoles` recipe now adds role and permission information into the access token payload by default. If you are already doing this manually, this will result in duplicate data in the access token.

-   You can disable this behaviour by setting `skip_adding_roles_to_access_token` and `skip_adding_permissions_to_access_token` to true in the recipe init.
-   Check how to use the new claims in the updated guide: https://supertokens.com/docs/userroles/protecting-routes


## [0.10.4] - 2022-08-30
## Features:
- Add support for User ID Mapping using `create_user_id_mapping`, `get_user_id_mapping`, `delete_user_id_mapping`, `update_or_delete_user_id_mapping` functions

## [0.10.3] - 2022-08-29

### Bug fix
- Send FORM_FIELD error with 200 status code instead of 500 on invalid request body or when user passes non-string values as email ID for `/auth/signin`

### Changes
- Add to test to ensure that overrides are applying correctly in methods called on SessionContainer instances

## [0.10.2] - 2022-07-14
### Bug fix
- Make `user_context` optional in userroles recipe syncio functions. 

## [0.10.1] - 2022-07-11

### Documentation:
- Added `pdoc` template files to project inside `docs-templates` directory
- Updated `build-docs` in Makefile to use `docs-templates` as the template directory while generating docs using `pdoc`
- Updated `html.mako` template to have a single `h1` tag and have a default meta description tag

### Changes
- Relax version requirements for `httpx`, `cryptography`, and `asgiref` to fix https://github.com/supertokens/supertokens-python/issues/207

## [0.10.0] - 2022-07-04

- Update tests to cover `resend_code` feature in `passwordless` and `thirdpartypasswordless` recipe.
- Update usermetadata tests to ensure that utf8 chars are supported.
- Mark tests as skipped if core version requirements are not met.
- Use [black](https://github.com/psf/black) instead of `autopep8` to format code.
- Add frontend integration tests for `django2x`

### Bug fix:

- Clears cookies when `revoke_session` is called using the session container, even if the session did not exist from before: https://github.com/supertokens/supertokens-node/issues/343

### Breaking changes:
- Change request arg type in session recipe functions from Any to BaseRequest.
- Changes session function recipe interfaces to not throw an `UNAUTHORISED` error when the input is a session_handle: https://github.com/supertokens/backend/issues/83
  - `get_session_information` now returns `None` if the session does not exist.
  - `update_session_data` now returns `False` if the input `session_handle` does not exist.
  - `update_access_token_payload` now returns `False` if the input `session_handle` does not exist.
  - `regenerate_access_token` now returns `None` if the input access token's `session_handle` does not exist.
  - The `session_class` functions have not changed in behaviour and still throw `UNAUTHORISED` error. This works cause the `session_class` works on the current session and not some other session.


### Features:
- Adds default `user_context` for API calls that contains the request object. It can be used in APIs / functions override like this:

```python
def apis_override_email_password(param: APIInterface):
    og_sign_in_post = param.sign_in_post

    async def sign_in_post(
        form_fields: List[FormField],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ):
        req = user_context.get("_default", {}).get("request")
        if req:
            # do something with the request

        return await og_sign_in_post(form_fields, api_options, user_context)

    param.sign_in_post = sign_in_post
    return param

def functions_override_email_password(param: RecipeInterface):
    og_sign_in = param.sign_in

    async def sign_in(email: str, password: str, user_context: Dict[str, Any]):
        req = user_context.get("_default", {}).get("request")
        if req:
            # do something with the request

        return await og_sign_in(email, password, user_context)

    param.sign_in = sign_in
    return param

init(
    ...,
    recipe_list=[
        emailpassword.init(
            override=emailpassword.InputOverrideConfig(
                apis=apis_override_email_password,
                functions=functions_override_email_password,
            )
        ),
        session.init(),
    ],
)
```


### Documentation
- Add more details in the `CONTRIBUTING.md` to make it beginner friendly.


## [0.9.1] - 2022-06-27
### Features:

- Introduce `userroles` recipe.
```python
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.recipe import userroles
from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions, add_role_to_user

init(
    supertokens_config=SupertokensConfig('http://localhost:3567'),
    app_info=InputAppInfo(
        app_name='SuperTokens Demo',
        api_domain='https://api.supertokens.io',
        website_domain='supertokens.io'
    ),
    framework='flask',
    recipe_list=[userroles.init()]
)

user_id = "userId"
role = "role"
permissions = ["perm1", "perm2"]

# Functions to use inside your views:
# Create a new role with a few permissions:
result = await create_new_role_or_add_permissions(role, permissions)
# Add role to the user:
result = await add_role_to_user(user_id, role)
# Check documentation for more examples..
```

## [0.9.0] - 2022-06-23
### Fixes
- Fixes Cookie same_site config validation.
- Remove `<Recipe>(Email|SMS)TemplateVars` in favour of `(Email|SMS)TemplateVars` for better DX.

### Breaking change
-   https://github.com/supertokens/supertokens-node/issues/220
    -   Adds `{status: "GENERAL_ERROR", message: string}` as a possible output to all the APIs.
    -   Changes `FIELD_ERROR` output status in third party recipe API to be `GENERAL_ERROR`.
    -   Replaced `FIELD_ERROR` status type in third party signinup API with `GENERAL_ERROR`.
    -   Removed `FIELD_ERROR` status type from third party signinup recipe function.
-   If sms or email sending failed in passwordless recipe APIs, we now throw a regular JS error from the API as opposed to returning a `GENERAL_ERROR` to the client.
-   If there is an error whilst getting the profile info about a user from a third party provider (in /signinup POST API), then we throw a regular JS error instead of returning a `GENERAL_ERROR` to the client.
- Make email and sms delivery ingredient interfaces developer friendly:
    - Remove the need of `SMSDeliveryTwilioConfig`, `EmailDeliverySMTPConfig`, and `SupertokensServiceConfig`.
    - Export `(.*)OverrideInput` and `(Email|SMS)DeliveryOverrideInput` from the relevant recipes.
    - Rename `Type<Recipe>EmailDeliveryInput` to `<Recipe>EmailTemplateVars`
    - Export `EmailTemplateVars` (alias of `<Recipe>EmailTemplateVars`) from all the relevant recipes
    - Export `PasswordlessLogin(Email|SMS)TemplateVars`, `PasswordResetEmailTemplateVars`, and `VerificationEmailTemplateVars` from relevant recipes.
    - Rename `(.*)ServiceConfig` to `(.*)Settings` for readability.
    - Rename arg `input_` to `template_vars` in `EmailDeliveryInterface.send_email` and `SMTPServiceInterface.send_sms` functions.
    - Rename arg `input_` to `content` and `template_vars` in `SMTPServiceInterface.send_raw_email` and `SMTPServiceInterface.get_content` functions respectively.
    - Rename arg `get_content_result` to `content` and `input_` to `template_vars` in `TwilioServiceInterface.send_raw_email` and `TwilioServiceInterface.get_content` functions respectively.
- Removes support for FDI < 1.14

### Changes
-   Changes `get_email_for_user_id` function inside thirdpartypasswordless to take into account passwordless emails and return an empty string in case a passwordless email doesn't exist. This helps situations where the dev wants to customise the email verification functions in the thirdpartypasswordless recipe.

## [0.8.4] - 2022-06-17
### Added

-   `email_delivery` user config for Emailpassword, Thirdparty, ThirdpartyEmailpassword, Passwordless and ThirdpartyPasswordless recipes.
-   `sms_delivery` user config for Passwordless and ThirdpartyPasswordless recipes.
-   `Twilio` service integartion for `sms_delivery` ingredient.
-   `SMTP` service integration for `email_delivery` ingredient.
-   `Supertokens` service integration for `sms_delivery` ingredient.

### Deprecated

-   For Emailpassword recipe input config, `reset_password_using_token_feature.create_and_send_custom_email` and `email_verification_feature.create_and_send_custom_email` have been deprecated.
-   For Thirdparty recipe input config, `email_verification_feature.create_and_send_custom_email` has been deprecated.
-   For ThirdpartyEmailpassword recipe input config, `reset_password_using_token_feature.create_and_send_custom_email` and `email_verification_feature.create_and_send_custom_email` have been deprecated.
-   For Passwordless recipe input config, `create_and_send_custom_email` and `createAndSendCustomTextMessage` have been deprecated.
-   For ThirdpartyPasswordless recipe input config, `create_and_send_custom_email`, `createAndSendCustomTextMessage` and `email_verification_feature.create_and_send_custom_email` have been deprecated.


### Migration

Following is an example of ThirdpartyPasswordless recipe migration. If your existing code looks like

```python
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.recipe import thirdpartypasswordless

async def send_pless_login_email(input_: TypePasswordlessEmailDeliveryInput, user_context: Dict[str, Any]):
    print("SEND_PLESS_LOGIN_EMAIL", input_.email, input_.user_input_code)

async def send_pless_login_sms(input_: TypeThirdPartyPasswordlessSmsDeliveryInput, user_context: Dict[str, Any]):
    print("SEND_PLESS_LOGIN_SMS", input_.phone_number, input_.user_input_code)

async def send_ev_verification_email(user: TpPlessUser, link: str, user_context: Any):
    print("SEND_EV_LOGIN_SMS", user.email, user.phone_number, user.third_party_info)


init(
    supertokens_config=SupertokensConfig('http://localhost:3567'),
    app_info=InputAppInfo(
        api_domain="...",
        app_name="...",
        website_domain="...",
    ),
    framework='...',
    recipe_list=[thirdpartypasswordless.init(
        contact_config=passwordless.ContactEmailOrPhoneConfig(
            create_and_send_custom_email=send_pless_login_email,
            create_and_send_custom_text_message=send_pless_login_sms,
        ),
        flow_type='...',
        email_verification_feature=thirdpartypasswordless.InputEmailVerificationConfig(
            create_and_send_custom_email=send_ev_verification_email,
        )
    )]
)
```

After migration to using new `email_delivery` and `sms_delivery` config, your code would look like:

```python
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryInterface, EmailDeliveryConfig
from supertokens_python.ingredients.smsdelivery.types import SMSDeliveryInterface, SMSDeliveryConfig
from supertokens_python.recipe import thirdpartypasswordless, passwordless

from supertokens_python.recipe.emailverification.types import TypeEmailVerificationEmailDeliveryInput


async def send_pless_login_email(input_: TypePasswordlessEmailDeliveryInput, user_context: Dict[str, Any]):
    print("SEND_PLESS_LOGIN_EMAIL", input_.email, input_.user_input_code)

async def send_pless_login_sms(input_: TypeThirdPartyPasswordlessSmsDeliveryInput, user_context: Dict[str, Any]):
    print("SEND_PLESS_LOGIN_SMS", input_.phone_number, input_.user_input_code)

async def send_ev_verification_email(user: TpPlessUser, link: str, user_context: Any):
    print("SEND_EV_LOGIN_SMS", user.email, user.phone_number, user.third_party_info)


class EmailDeliveryService(EmailDeliveryInterface):
    async def send_email(self, input_: TypeThirdPartyPasswordlessEmailDeliveryInput, user_context: Dict[str, Any]):
        if isinstance(input_, TypeEmailVerificationEmailDeliveryInput):
            await send_ev_verification_email(input_, user_context)
        elif isinstance(input_, TypePasswordlessEmailDeliveryInput):
            await send_pless_login_email(input_, user_context)

class SMSDeliveryService(SMSDeliveryInterface):
    async def send_sms(self, input_: TypeThirdPartyPasswordlessSmsDeliveryInput, user_context: Dict[str, Any]):
        await send_pless_login_sms(input_, user_context)

init(
    supertokens_config=SupertokensConfig('http://localhost:3567'),
    app_info=InputAppInfo(
        app_name="...",
        api_domain="...",
        website_domain="...",
    ),
    framework='...',
    recipe_list=[thirdpartypasswordless.init(
        contact_config=passwordless.ContactEmailOrPhoneConfig(),
        flow_type='...',
        email_delivery=EmailDeliveryConfig(
            service=EmailDeliveryService(),
        ),
        sms_delivery=SMSDeliveryConfig(
            service=SMSDeliveryService(),
        ),
    )]
)
```

## [0.8.3] - 2022-06-09
- Fix bugs in syncio functions across all the recipes
- Fixes bug in resend code POST API in passwordless recipe to use the correct instance type during checks.
- Fixes bug in thirdpartypasswordless recipe to prevent infinite loop during resent code API

## [0.8.2] - 2022-05-27
- Update phonenumbers lib dependency version
- Adds type checks to the parameters of the emailpassword init funtion.
- Adds type checks to the parameters of the emailverification init funtion.
- Adds type checks to the parameters of the jwt init funtion.
- Adds type checks to the parameters of the openid init funtion.
- Adds type checks to the parameters of the session init funtion.
- Adds type checks to the parameters of the passwordless init funtion.
- Adds type checks to the parameters of the thirdparty init funtion.
- Adds type checks to the parameters of the thirdpartyemailpassword init funtion.
- Adds type checks to the parameters of the thirdpartypasswordless init funtion.
- Adds type checks to the parameters of the usermetadata init funtion.
- Adds django with thirdpartyemailpassword example.

## [0.8.1]
- Fixed execute_async to check and use asyncio mode.
- Ignores any exception from send_telemetry, not to prevent the app from starting up.

## [0.8.0]
- Updates `RecipeInterface` and `APIInterface` methods to return exact return types instead of abstract base types, for the emailpassword recipe.
- Updates `RecipeInterface` and `APIInterface` methods to return exact return types instead of abstract base types, for the thirdparty recipe.
- Updates `RecipeInterface` and `APIInterface` methods to return exact return types instead of abstract base types, for the passwordless recipe.
- Updates `RecipeInterface` and `APIInterface` methods to return exact return types instead of abstract base types, for the openid recipe.
- Updates `RecipeInterface` and `APIInterface` methods to return exact return types instead of abstract base types, for the JWT recipe.
- Updates `RecipeInterface` and `APIInterface` methods to return exact return types instead of abstract base types, for the session recipe.
- Updates `RecipeInterface` methods to return exact return types instead of abstract base types, for the usermetadata recipe.
- Adds `EmailPasswordSignInOkResult`, `EmailPasswordSignUpOkResult` and `ThirdPartySignInUpOkResult` to use the thirdpartyemailpassword recipe's `User` class.
- Adds `ThirdPartySignInUpPostOkResult`, `EmailPasswordSignInPostOkResult` and `EmailPasswordSignUpPostOkResult` to use the thirdpartyemailpassword recipe's `User` class.
- Renames wrongly named `ResetPasswordUsingTokenWrongUserIdErrorResult` to `ResetPasswordUsingTokenInvalidTokenError`, one of the return types of `reset_password_using_token` method in the `RecipeInterface`.
- Removes unused classes `GeneratePasswordResetTokenResponse`, `EmailExistsResponse` and `PasswordResetResponse`.
- Removed `third_party_info` from emailpassword `User` class.
- Exports re-used Result and Response classes from `thirdparty` & `emailpassword` recipe interfaces in the `thirdpartyemailpassword` recipe interfaces.
- Exports re-used Result and Response classes from `thirdparty` & `passwordless` recipe interfaces in the `thirdpartypasswordless` recipe interfaces.
- Renames `*ErrorResult` classes to `*Error`.
- Renames `*ErrorResponse` classes to `*Error`.
- Renames `*OkResponse` classes to `*OkResult`.
- Renames `*ResultOk` classes to `*OkResult`.

## [0.7.3] - 2022-05-12
- Fixed execute_async to check and use asyncio mode.
- Ignores any exception from send_telemetry, not to prevent the app from starting up.

## [0.7.2] - 2022-05-08
- Bug fix in telemetry data API

## [0.7.1] - 2022-05-06
- Updates Project Setup, Modifying Code and Testing sections in the contributing guide
- Fixed async execution of `send_telemetry` in init and `call_get_handshake_info` in session recipe implementation.
- Fixed `Content-length` in FastAPI Response wrapper.

## [0.7.0] - 2022-04-28
- Changes third party provider type to get client ID dynamically so that it can be changed based on user context.

## [0.6.7] - 2022-04-23
- Adds delete email (`delete_email_for_user`) and phone number (`delete_phone_number_for_user`) functions for passwordless and thirdpartypasswordless recipe
- Adds check for user type in update passwordless info in thirdpartypasswordless recipe

## [0.6.6] - 2022-04-22
- Fixes issue in user metadata recipe where as are exposing async functions in the syncio file.

## [0.6.5] - 2022-04-18
- Upgrade and freeze pyright version
- Rename `compare_version` to `get_max_version` for readability
- Add user metadata recipe

## [0.6.4] - 2022-04-11
- bug fix in `default_create_and_send_custom_email` for emailverification recipe where we were not sending the email if env var was not set.
- Fix telemetry issues related to asyncio when using FastAPI. Related issue: https://github.com/supertokens/supertokens-core/issues/421
- adds git action for running tests

## [0.6.3] - 2022-04-09
- Setup logging for easier debugging
- Adds github action for checking all things checked by pre commit hook

## [0.6.2] - 2022-04-07
- Fix Passwordless OTP recipe phone number field to fix https://github.com/supertokens/supertokens-core/issues/416

## [0.6.1] - 2022-03-29

- Expands allowed version range for httpx library to fix https://github.com/supertokens/supertokens-python/issues/98

## [0.6.0] - 2022-03-26

### Changes
- Removes dependency on framework specific dependencies (`werkzeug` and `starlette`)

### Breaking change:
- Import for fastapi middleware:
   - Old
      ```
      from supertokens_python.framework.fastapi import Middleware

      app = FastAPI()
      app.add_middleware(Middleware)
      ```
   - New
      ```
      from supertokens_python.framework.fastapi import get_middleware

      app = FastAPI()
      app.add_middleware(get_middleware())
      ```

### Fixes
- `user_context` was passed incorrectly to the `create_new_session_function`.

## [0.5.3] - 2022-03-26
### Fixes
- Bug in user pagination functions: https://github.com/supertokens/supertokens-python/issues/95


## [0.5.2] - 2022-03-17
### Fixes
- https://github.com/supertokens/supertokens-python/issues/90
- Thirdpartypasswordless recipe + tests

### Changed:
- Added new function to BaseRequest class called `set_session_as_none` to set session object to None.

## [0.5.1] - 2022-03-02

### Fixes:
- Bug where a user had to add dependencies on all frameworks when using the SDK: https://github.com/supertokens/supertokens-python/issues/82

## [0.5.0] - 2022-02-03

### Breaking Change
- User context property added for all recipes' apis and functions
- Removes deprecated functions in recipe for user pagination and user count
- Changed email verification input functions' user type in emailpassword to be equal to emailpassword's user and not emailverification user.
- All session recipe's error handler not need to return `BaseResponse`.
- Session's recipe `get_session_information` returns a `SessionInformationResult` class object instead of a `dict` for easier consumption.
- `get_link_domain_and_path` config in passwordless recipe now takes a class type input as opposed to a string input as the first param
- Renamed `Session` to `SessionContainer` in session
- Upgrades `typing_extensions` to version 4.1.1
- Renames functions in ThirdPartyEmailPassword recipe (https://github.com/supertokens/supertokens-node/issues/219):
    -   Recipe Interface:
        -   `sign_in_up` -> `thirdparty_sign_in_up`
        -   `sign_up` -> `emailpassword_sign_up`
        -   `sign_in` -> `emailpassword_sign_in`
    -   API Interface:
        -   `email_exists_get` -> `emailpassword_email_exists_get`
    -   User exposed functions (in `recipe/thirdpartyemailpassword/asyncio` and `recipe/thirdpartyemailpassword/syncio`)
        -   `sign_in_up` -> `thirdparty_sign_in_up`
        -   `sign_up` -> `emailpassword_sign_up`
        -   `sign_in` -> `emailpassword_sign_in`

### Added
- Returns session from all APIs where a session is created
- Added `regenerate_access_token` as a new recipe function for the session recipe.
- Strong typings.

### Change
- Changed async_to_sync_wrapper.py file to make it simpler
- Remove default `= None` for functions internal to the package

### Bug fix:
- If logging in via social login and the email is already verified from the provider's side, it marks the email as verified in SuperTokens core.
- Corrects how override is done in thirdpartyemailpassword recipe and API implementation

## [0.4.1] - 2022-01-27

### Added
-   add workflow to verify if pr title follows conventional commits

### Changed
- Added userId as an optional property to the response of `recipe/user/password/reset` (compatibility with CDI 2.12).
- Adds ability to give a path for each of the hostnames in the connectionURI: https://github.com/supertokens/supertokens-node/issues/252

### Fixed
- Bug fixes in Literal import which caused issues when using the sdk with python version 3.7.
- Fixes https://github.com/supertokens/supertokens-node/issues/244 - throws an error if a user tries to update email / password of a third party login user.

## [0.4.0] - 2022-01-09

### Added
-   Adds passwordless recipe
-   Adds compatibility with FDI 1.12 and CDI 2.11

## [0.3.1] - 2021-12-20

### Fixes
- Bug in ThirdpartyEmailpassword recipe init function when InputSignUpFeature is not passed.

### Added
- delete_user function
- Compatibility with CDI 2.10

## [0.3.0] - 2021-12-10

### Breaking Change
- Config changes

### Added
- Added `mode` config for FastAPI which now supports both `asgi` and `wsgi`.
- The ability to enable JWT creation with session management, this allows easier integration with services that require JWT based authentication: https://github.com/supertokens/supertokens-core/issues/250
- You can do BaseRequest.request to get the original request object. Fixes #61


## [0.2.3] - 2021-12-07
### Fixes

- Removes use of apiGatewayPath from apple's redirect URI since that is already there in the apiBasePath


## [0.2.2] - 2021-11-22

### Added
- Sign in with Discord, Google workspaces.

### Changes
- Allow sending of custom response: https://github.com/supertokens/supertokens-node/issues/197
- Change `set_content` to `set_json_content` in all the frameworks
- Adds `"application/json; charset=utf-8"` header to json responses.

## [0.2.1] - 2021-11-10

### Changes
- When routing, ignores `rid` value `"anti-csrf"`: https://github.com/supertokens/supertokens-python/issues/54
- `get_redirect_uri` function added to social providers in case we set the `redirect_uri` on the backend.
- Adds optional `is_default` param to auth providers so that they can be reused with different credentials.
- Verifies ID Token sent for sign in with apple as per https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_rest_api/verifying_a_user
- Removes empty awslambda folder from framework
- If json parsing fails in the frameworks, catches those exceptions and returns an empty object.

## [0.2.0] - 2021-10-22

### Breaking change
- Removes `sign_in_up_post` from thirdpartyemailpassword API interface and replaces it with three APIs: `email_password_sign_in_post`, `email_password_sign_up_post` and `third_party_sign_in_up_post`: https://github.com/supertokens/supertokens-node/issues/192
- Renames all "jwt" related functions in session recipe to use "access_token" instead
- jwt recipe and unit tests
- Support for FDI 1.10: Allow thirdparty `/signinup POST` API to take `authCodeResponse` XOR `code` so that it can supprt OAuth via PKCE
- Apple provider disabled for now

### Bug Fixes
- Bug fix: https://github.com/supertokens/supertokens-python/issues/42
- Bug fix: https://github.com/supertokens/supertokens-python/issues/10
- Bug fix: https://github.com/supertokens/supertokens-python/issues/13

## [0.1.0] - 2021-10-18
### Changes
- all the user facing async functions now needs to be imported from asyncio sub directory. For example, importing the async implementation of create_new_session from session recipe has changed from:
    ```python3
    from supertokens_python.recipe.session import create_new_session
    ```
    to:
    ```python3
    from supertokens_python.recipe.session.asyncio import create_new_session
    ```
- sync versions of the functions are now needs to be imported from syncio directory instead of the sync directory
- all the license comments now uses single line comment structure instead of multi-line comment structure

### Added
- auth-react tests for flask and django
- if running django in async way, set `mode` to `asgi` in `config`

## [0.0.3] - 2021-10-13
### Added
- Adds OAuth development keys for Google and Github for faster recipe implementation.
- Removed the Literal from python 3.8 and added Literal from typing_extensions package. Now supertokens_python can be used with python 3.7 .


## [0.0.2] - 2021-10-09
### Fixes
- dependency issues for frameworks

## [0.0.1] - 2021-09-10
### Added
- Multiple framework support. Currently supporting Django, Flask(1.x) and Fastapi.
- BaseRequest and BaseResponse interfaces which are used inside recipe instead of previously used Response and Request from Fastapi.
- Middleware, error handlers and verify session for each framework.
- Created a wrapper for async to sync for supporting older version of python web frameworks.
- Base tests for each framework.
- New requirements in the setup file. 
