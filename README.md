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
Additionally, if you choose to use a proxy, ensure that the 'method' arguement is set correctly, you can find these in the official documentation: https://docs.capsolver.com/ for each captcha type

### WIP
Currently only supports:
* async

Watch this space for future additions
