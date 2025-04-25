from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import asyncio

class AuthAgent(Agent):
    class AuthBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=60)
            if msg:
                print("[AuthAgent] Received URLs to test for login.")
                urls = msg.body.strip().split("\n")
                for url in urls:
                    if self.looks_like_login(url):
                        await self.try_login(url)
            else:
                print("[AuthAgent] No message received. Retrying...")

        def looks_like_login(self, url):
            """Heuristic: look for URLs that seem like login pages."""
            login_keywords = ["login", "signin", "auth", "account"]
            return any(kw in url.lower() for kw in login_keywords)

        async def try_login(self, url):
            print(f"[AuthAgent] Attempting login on {url}")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as resp:
                        html = await resp.text()
                        soup = BeautifulSoup(html, "html.parser")
                        form = soup.find("form")
                        if not form:
                            print(f"[AuthAgent] No form found on {url}")
                            return

                        action = form.get("action") or url
                        method = form.get("method", "get").lower()
                        inputs = {inp.get("name"): "admin" for inp in form.find_all("input") if inp.get("name")}

                        if method == "post":
                            login_url = action if action.startswith("http") else f"{urlparse(url).scheme}://{urlparse(url).netloc}/{action.lstrip('/')}"
                            async with session.post(login_url, data=inputs, timeout=10) as login_resp:
                                if login_resp.status == 200:
                                    print(f"[AuthAgent] Login POST to {login_url} returned 200")
                                    await self.report_finding(f"[Auth] Attempted login on: {url}")
            except Exception as e:
                print(f"[AuthAgent] Error on {url}: {e}")

        async def report_finding(self, finding):
            msg = Message(to="reporter_agent@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = finding
            await self.send(msg)
            print(f"[AuthAgent] Reported finding to ReporterAgent: {finding}")

    async def setup(self):
        print("[AuthAgent] Agent launched.")
        self.add_behaviour(self.AuthBehaviour())
