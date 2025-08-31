import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        # response = await session.post('http://localhost:8080/api/v1/advertisements',
        #                               json={"title": "1", "description": "2", "owner": "3"})
        # print(response.status)
        # print(await response.text())

        response = await session.get('http://localhost:8080/api/v1/advertisements/1')
        print(response.status)
        print(await response.text())

        # response = await session.patch('http://localhost:8080/api/v1/advertisements/1',
        #                               json={"title": "2", "description": "3", "owner": "4"})
        # print(response.status)
        # print(await response.text())

        # response = await session.delete('http://localhost:8080/api/v1/advertisements/1')
        # print(response.status)
        # print(await response.text())


asyncio.run(main())
