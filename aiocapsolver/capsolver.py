import base64
import aiofiles
import aiohttp
from captcha_error import CaptchaError


class AsyncCapSolver:
    __session = None

    def __init__(self, api_key: str, retry_interval=0.2):
        self.api_key = api_key
        self.retry_interval = 0.2

    async def close(self):
        await self.__session.close()
        self.__session = None

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
        return await self.__submit_task('ImageToTextTask', body=base64_data, module=module, score=minimum_confidence,
                                        case=case)

    async def solve_cloudflare_turnstile(self, url: str, site_key: str, proxy: str, action: str = None,
                                         cdata: str = None):
        metadata = {
            'type': 'turnstile',
            'action': action,
            'cdata': cdata
        }
        return await self.__submit_task('AntiCloudflareTask', webSiteURL=url, webSiteKey=site_key, proxy=proxy,
                                        metadata=metadata)

    async def __submit_task(self, type: str, app_id=None, **kwargs):

        data = {
            # "appId": app_id,
            "task": {
                "type": type,
            }
        }

        data['task'].update(kwargs)

        return await self.__post('createTask', data)

    async def __post(self, endpoint, data=None) -> dict:
        if data is None:
            data = {}

        data['clientKey'] = self.api_key

        if not self.__session:
            await self.__create_session()

        headers = {
            'Content-Type': 'application/json'
        }

        async with self.__session.post('https://api.capsolver.com/' + endpoint, headers=headers, json=data) as r:
            j = await r.json()

        if j['errorId'] == 1:
            raise (CaptchaError(j['errorCode'], j['errorDescription']))

        task_id = j.get('taskId')
        status = j.get('status')

        if status == 'ready':
            return j.get('solution')

        if status == 'idle':
            return await self.__get_task_result(task_id)

        if status == 'processing':
            return await self.__get_task_result(task_id, self.retry_interval)  # wait 200 ms in between subsequent requests

    async def __get_task_result(self, task_id, timeout=0):
        if timeout:
            await asyncio.sleep(timeout)
        data = {
            'taskId': task_id
        }
        return await self.__post('getTaskResult', data)  # Recursively calls until complete


async def main():
    api_key = os.environ.get('API_KEY')
    proxy = os.environ.get('PROXY')
    url = os.environ.get('TESTING_URL')
    sitekey = os.environ.get('TESTING_SITEKEY')
    solver = AsyncCapSolver(api_key)
    print(await solver.solve_cloudflare_turnstile(url, sitekey, proxy))
    await solver.close()


if __name__ == '__main__':
    import os
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
