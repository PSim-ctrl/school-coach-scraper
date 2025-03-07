import asyncio
import aiohttp
import requests

class AsyncRequester:
    async def fetch(self, session, url):
        """Fetch a URL using aiohttp"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        async with session.get(url, headers=headers) as response:
            return await response.text('utf-8', errors='ignore'), url

    async def main(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, url) for url in urls]
            responses = await asyncio.gather(*tasks)
            return responses
            # for i, response in enumerate(responses):
            #     print(f"Response {i + 1}: {response[:100]}...")  # Print first 100 chars

    def run(self, urls):
        return asyncio.run(self.main(urls))
    
    def get(url):
        try:
            content = None
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }
            req = requests.get(url, headers=headers)
        
            if req.status_code == 200:
                content = req.text

            return content
        except:
            return None

