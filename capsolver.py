import aiohttp
import aiofiles
import json
import base64
from captcha_error import CaptchaError


class AsyncCapSolver:
    __session = None
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def __create_session(self):
        if self.__session is aiohttp.ClientSession:
            await self.__session.close
        self.__session = aiohttp.ClientSession()

    async def get_balance(self) -> float:
        data = await self.__post('getBalance')
        return data['balance']

    async def get_packages(self) -> list:
        data = await self.__post('getBalance')
        return data['balance']

    async def solve_image_to_text(self, filepath, module='common', minimum_confidence=0.8, case=True):
        async with aiofiles.open(filepath, mode='rb') as file:
            image_data = await file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        await self.__submit_task('ImageToTextTask', body=base64_data, module=module, score=minimum_confidence, case=case)






    async def __submit_task(self, type: str, app_id=None, **kwargs):

        data = {
            #"appId": app_id,
            "task": {
                "type":type,
            }
        }

        data['task'].update(kwargs)
        print(json.dumps(data, indent=4))

        response = await self.__post('createTask', data)




    async def __post(self, endpoint, data=None) -> dict:
        if data is None:
            data = {}

        data['clientKey'] = self.api_key

        if self.__session is not aiohttp.ClientSession:
            await self.__create_session()

        headers = {
            'Content-Type': 'application/json'
        }

        r = await self.__session.post('https://api.capsolver.com/' + endpoint, headers=headers, json=data)
        print(r.status)
        print(r.content_type)
        print(await r.text())
        j = await r.json()

        if j['errorId'] == 1:
            raise(CaptchaError(j['errorCode'], j['errorDescription']))
        else:
            return j







async def main():
    api_key = os.environ.get('API_KEY')
    solver = AsyncCapSolver(api_key)
    await solver.solve_image_to_text('testing/captcha.png')


if __name__ == '__main__':
    import os
    import asyncio
    asyncio.run(main())
