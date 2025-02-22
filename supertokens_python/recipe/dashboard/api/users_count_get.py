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
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from supertokens_python.framework import BaseResponse
from supertokens_python.supertokens import Supertokens

if TYPE_CHECKING:
    from supertokens_python.recipe.dashboard.interfaces import (
        APIOptions,
        APIInterface,
    )

from supertokens_python.utils import send_200_response


async def handle_users_count_get_api(
    _: APIInterface, api_options: APIOptions
) -> Optional[BaseResponse]:
    count = await Supertokens.get_instance().get_user_count(include_recipe_ids=None)

    return send_200_response({"status": "OK", "count": count}, api_options.response)
