# Capsolver.com API for Python
aioCapsolver is an elegant python implementation of the Capsolver.com API

### Features:
* Async/Sync support(soon)
* All endpoints/inputs
* Error handling

### Installation
```pip install aiocapsolver```
(https://pypi.org/project/aiocapsolver/)
### Usage

```python
from aiocapsolver.capsolver import AsyncCapSolver

solver = AsyncCapSolver(MyCapSolverApiKey)


async def myasyncfunction():
    result = await solver.solve_image_to_text(images/myimage.png)
    # This works the same for a task that we have to await the result for, it is done automatically!
    result = await solve.solve_cloudflare_turnstile(url, site_key, proxy)
```

Note that some functions **require** a proxy!
Additionally, if you choose to use a proxy, ensure that the 'method' arguement is set correctly, i.e if you want to use a proxy:
```
await solver.solve_hcaptcha(url, site_key, proxy='http://user:pass@my_proxy:1234',method='HCaptchaTurboTask')
```
as oppsoed to method = 'HCaptchaTurboTaskProxyLess'

you can find these in the official documentation: https://docs.capsolver.com/ for each captcha type. It's possible I will make the library automatically choose the method in the future.

### WIP
Currently only supports:
* async
* certain features are subject to change, for example, I may create a 'Solution' object that is returned with each solve method, instead of the current dictionary, so that the token/text/etc. can have a consistent key like `Solution.solution`, instead of `solution['token']` or `solution['text']`

Watch this space for future additions
