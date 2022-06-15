# Copyright (c) 2021, VRAI Labs and/or its affiliates. All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0 (the
# "License") as published by the Apache Software Foundation.
#
# You may not use this file except in compliance with the License. You may
# obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import io
import json
from contextlib import redirect_stdout
from typing import Any, Dict, Union
from unittest.mock import MagicMock

import httpx
import requests
import requests_mock
import respx
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.testclient import TestClient
from pytest import fixture, mark
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.ingredients.smsdelivery.services.supertokens import \
    SUPERTOKENS_SMS_SERVICE_URL
from supertokens_python.ingredients.smsdelivery.services.twilio import (
    GetContentResult, ServiceInterface, SMSDeliveryTwilioConfig,
    TwilioServiceConfig)
from supertokens_python.ingredients.smsdelivery.types import (
    SMSDeliveryConfig, SMSDeliveryInterface)
from supertokens_python.recipe import passwordless, session
from supertokens_python.recipe.passwordless.smsdelivery.services.supertokens import \
    SuperTokensService
from supertokens_python.recipe.passwordless.smsdelivery.services.twilio import \
    TwilioService
from supertokens_python.recipe.passwordless.types import \
    TypePasswordlessSmsDeliveryInput
from tests.utils import (app_info, clean_st, reset, setup_st,
                         sign_in_up_request_phone, sms_delivery_twilio_config,
                         start_st, supertokens_config)

respx_mock = MagicMock()


def setup_function(_):
    reset()
    clean_st()
    setup_st()


def teardown_function(_):
    reset()
    clean_st()


@fixture(scope='function')
async def driver_config_client():
    app = FastAPI()
    app.add_middleware(get_middleware())

    @app.get('/login')
    async def login(_request: Request):  # type: ignore
        user_id = 'userId'
        # await create_new_session(request, user_id, {}, {})
        return {'userId': user_id}

    return TestClient(app)


@mark.asyncio
async def test_pless_login_default_backward_compatibility(driver_config_client: TestClient):
    "Passwordless login: test default backward compatibility api being called"

    init(
        supertokens_config=supertokens_config,
        app_info=app_info,
        framework='fastapi',
        recipe_list=[passwordless.init(
            contact_config=passwordless.ContactPhoneOnlyConfig(),
            flow_type="USER_INPUT_CODE_AND_MAGIC_LINK",
        ), session.init()]
    )
    start_st()
    

    resp = sign_in_up_request_phone(driver_config_client, "+917481897215", True)



@mark.asyncio
async def test_pless_login_sms_delivery_supertokens(driver_config_client: TestClient):
    "Passwordless login: test supertokens SMS api being called"

    init(
        supertokens_config=supertokens_config,
        app_info=app_info,
        framework='fastapi',
        recipe_list=[passwordless.init(
            contact_config=passwordless.ContactPhoneOnlyConfig(),
            flow_type="USER_INPUT_CODE_AND_MAGIC_LINK",
            sms_delivery=SMSDeliveryConfig(
                service=SuperTokensService(
                    config=SupertokensServiceConfig(api_key="SOME_KEY")
                )
            )
        ), session.init()]
    )
    start_st()
    

    resp = sign_in_up_request_phone(driver_config_client, "+917481897215", True)



@mark.asyncio
async def test_pless_login_twilio_service(driver_config_client: TestClient):
    "Passwordless login: test twilio service"

    twilio_sms_delivery_service = TwilioService(
        config=sms_delivery_twilio_config
    )

    init(
        supertokens_config=supertokens_config,
        app_info=app_info,
        framework='fastapi',
        recipe_list=[passwordless.init(
            contact_config=passwordless.ContactPhoneOnlyConfig(),
            flow_type="USER_INPUT_CODE_AND_MAGIC_LINK",
            sms_delivery=SMSDeliveryConfig(
                service=twilio_sms_delivery_service,
            )
        ), session.init()]
    )
    start_st()

    resp = sign_in_up_request_phone(driver_config_client, "+917481897215", True)
