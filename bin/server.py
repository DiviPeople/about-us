# Copyright (C) 2020 Dmitry Ivanko. All Rights Reserved.
# Copyright (C) 2020 Vladislav Yarovoy. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Server-side of About-Us. """

import logging

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request

from about_us import config
from about_us import exceptions

logging.basicConfig(filename=config.LOG_PATH, level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class Handler(web.View):
    """Class-based handler of the requests for organization info. """

    def __init__(self, request: Request):
        super().__init__(request)

        self._organization_name = ''
        self.session = aiohttp.ClientSession()

    async def get(self):
        """Return all public info about organization from github. """

        if 'organizationName' in self.request.query:
            self._organization_name = self.request.query['organizationName']
        else:
            await self.session.close()

            return web.json_response(status=400)

        info = {
            'organization': await self.get_organization_info(),
            'members': await self.get_members(),
            'repos': await self.get_organization_repos()
        }
        await self.session.close()

        if None in info.values():
            return web.json_response(status=429)

        return web.json_response(info)

    async def get_organization_repos(self):
        """Request and return organization's repositories. """

        try:
            if self.session.closed:
                raise exceptions.SessionIsClosed
        except exceptions.SessionIsClosed:
            return None

        repositories = []

        try:
            async with self.session.get(url=f'https://api.github.com/orgs/'
                                            f'{self._organization_name}/repos') as resp:
                content = await resp.json()
        except aiohttp.client_exceptions.ClientConnectorError:
            LOGGER.error('Could not connect to GitHub API when request repos')
            return None

        try:
            if 'message' and 'documentation_url' in content:
                raise exceptions.RequestLimitExceeded
        except exceptions.RequestLimitExceeded:
            await self.session.close()

            return None

        for repo in content:
            repositories.append({
                'name': repo['name'],
                'description': repo['description'],
                'star_count': repo['stargazers_count'],
                'url': repo['html_url']
            })

        return repositories

    async def get_organization_info(self):
        """Request and return info of the organization. """

        try:
            if self.session.closed:
                raise exceptions.SessionIsClosed
        except exceptions.SessionIsClosed:
            LOGGER.error('Request limit exceeded to GitHub API.')
            return None

        try:
            async with self.session.get(url=f'https://api.github.com/orgs/'
                                            f'{self._organization_name}') as resp:
                content = await resp.json()
        except aiohttp.client_exceptions.ClientConnectorError:
            LOGGER.error('Could not connect to GitHub API when request info')
            return None

        try:
            if 'message' and 'documentation_url' in content:
                raise exceptions.RequestLimitExceeded
        except exceptions.RequestLimitExceeded:
            await self.session.close()
            return None

        return {
            'name': content['name'] != '' and content['name'] or content['login'],
            'description': content['description'],
            'url': content['html_url']
        }

    async def get_members(self):
        """Request and return organization's members. """

        members = []

        try:
            if self.session.closed:
                raise exceptions.SessionIsClosed
        except exceptions.SessionIsClosed:
            return None

        try:
            async with self.session.get(url=f'https://api.github.com/orgs/'
                                            f'{self._organization_name}/members') as resp:
                content = await resp.json()
        except aiohttp.client_exceptions.ClientConnectorError:
            LOGGER.error('Could not connect to GitHub API when request members')
            return None

        try:
            if 'message' and 'documentation_url' in content:
                raise exceptions.RequestLimitExceeded
        except exceptions.RequestLimitExceeded:
            await self.session.close()
            return None

        for user in content:
            async with self.session.get(url=f'{user["url"]}') as resp:
                user_attrs = await resp.json()

            members.append({
                'name': user_attrs['name'] != '' and user_attrs['name'] or user['login'],
                'avatar_url': user['avatar_url'],
                'bio': user_attrs['bio'],
                'url': user['html_url']
            })

        return members


async def main():
    """The main entry point. """

    app = web.Application()
    app.router.add_get('/about_us/get_organization_info/', Handler)
    return app


if __name__ == '__main__':
    web.run_app(main(), host=config.HOST, port=config.PORT)
