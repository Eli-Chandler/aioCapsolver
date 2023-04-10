import base64

import aiofiles
import aiohttp

from aiocapsolver.captcha_error import CaptchaError


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
        data = await self.__post('getBalance', no_task=True)
        return data['balance']

    async def get_packages(self) -> list:
        data = await self.__post('getBalance', no_task=True)
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

    async def solve_cloudflare_5_second_challenge(self, url: str, site_key: str, proxy: str, html: str, action: str = None,
                                                  cdata: str = None):
        metadata = {
            'type': 'challenge',
            'action': action,
            'cdata': cdata
        }
        return await self.__submit_task('AntiCloudflareTask', webSiteURL=url, webSiteKey=site_key, proxy=proxy,
                                        metadata=metadata, html=html)

    async def solve_hcaptcha(self, url: str, site_key: str, method: str = 'HCaptchaTurboTaskProxyLess', is_invisible: bool = None, proxy: str = None, proxy_is_ipv6: bool = None,
                             enterprise_payload: dict = None, user_agent: str = None):
        return await self.__submit_task(method,
                                        websiteUrl=url,
                                        websiteKey=site_key,
                                        isInvisible=is_invisible,
                                        proxy=proxy,
                                        enableIPV6=proxy_is_ipv6,
                                        enterprisePayload=enterprise_payload,
                                        userAgent=user_agent)

    async def solve_funcaptcha(self, url, site_public_key, method='FunCaptchaTask', funcaptcha_api_js_subdomain=None, data=None, proxy=None):
        return await self.__submit_task(method,
                                        websiteURL=url,
                                        websitePublicKey=site_public_key,
                                        funcaptchaApiJSSubdomain=funcaptcha_api_js_subdomain,
                                        data=data,
                                        proxy=proxy)

    async def solve_geetest(self, url: str, gt_field: str, method='GeeTestTaskProxyLess', challenge: str = None, captcha_id: str = None, geetest_api_server_subdomain: str = None, proxy: str = None):
        return await self.__submit_task(method,
                                        websiteURL=url,
                                        gt=gt_field,
                                        challenge=challenge,
                                        captchaId=captcha_id,
                                        geetestApiServerSubdomain=geetest_api_server_subdomain,
                                        proxy=proxy)

    async def solve_recaptcha_v2(self, url: str, site_key: str, method: str = 'ReCaptchaV2TaskProxyLess', proxy: str = None, enterprise_payload: dict = None, is_invisible: bool = None,
                                 api_domain: str = None, user_agent: str = None, cookies: list = None):
        return await self.__submit_task(method,
                                        websiteURL=url,
                                        websiteKey=site_key,
                                        proxy=proxy,
                                        enterprisePayload=enterprise_payload,
                                        isInvisible=is_invisible,
                                        apiDomain=api_domain,
                                        userAgent=user_agent,
                                        cookies=cookies)

    async def solve_recaptcha_v3(self, url: str, site_key: str, page_action: str, method: str = 'ReCaptchaV3TaskProxyLess', minimum_score: float = None, proxy: str = None,
                                 enterprise_payload: dict = None, api_domain: str = None, user_agent: str = None, cookies: list = None):
        return await self.__submit_task(method,
                                        websiteURL=url,
                                        websiteKey=site_key,
                                        pageAction=page_action,
                                        minScore=minimum_score,
                                        proxy=proxy,
                                        enterprisePayload=enterprise_payload,
                                        apiDomain=api_domain,
                                        userAgent=user_agent,
                                        cookies=cookies)

    async def solve_mtcaptcha(self, url: str, site_key: str, proxy: str):
        await self.__submit_task('MtCaptchaTask',
                                 websiteURL=url,
                                 websiteKey=site_key,
                                 proxy=proxy)

    async def solve_datadome(self, url, captcha_url, proxy, user_agent):
        await self.__submit_task('DatadomeSliderTask',
                                 websiteURL=url,
                                 captchaUrl=captcha_url,
                                 proxy=proxy,
                                 userAgent=user_agent)

    async def __submit_task(self, type: str, app_id=None, **kwargs):

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        data = {
            # "appId": app_id,
            "task": {
                "type": type,
            }
        }

        data['task'].update(kwargs)

        return await self.__post('createTask', data)

    async def __post(self, endpoint, data=None, no_task=False) -> dict:
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

        if no_task == True:
            return j

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
    print(await solver.get_balance())
    print(await solver.solve_cloudflare_turnstile(url, sitekey, proxy))
    await solver.close()


if __name__ == '__main__':
    import os
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
