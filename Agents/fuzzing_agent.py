from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import aiohttp
import asyncio

class FuzzingAgent(Agent):
    class FuzzingBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.fuzzed_hosts = set()  # Avoid duplicate directory fuzz
            self.payloads = [
                "' OR '1'='1",
                "<script>alert(1)</script>",
                "../../etc/passwd",
                "'; DROP TABLE users; --"
            ]

        async def run(self):
            msg = await self.receive(timeout=60)
            if msg:
                print("[FuzzingAgent] Received URLs to fuzz.")
                urls = msg.body.strip().split("\n")
                for url in urls:
                    parsed = urlparse(url)
                    if parsed.query:
                        await self.parameter_fuzz(url)
                    else:
                        await self.directory_fuzz(url)
            else:
                print("[FuzzingAgent] No message received. Retrying...")

        async def parameter_fuzz(self, url):
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)

            for param in qs:
                for payload in self.payloads:
                    new_params = qs.copy()
                    new_params[param] = payload
                    new_query = urlencode(new_params, doseq=True)
                    test_url = urlunparse(parsed._replace(query=new_query))
                    print(f"[FuzzingAgent] Starting parameter fuzz on {test_url}")

                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(test_url, timeout=10) as resp:
                                body = await resp.text()

                                if payload in body:
                                    await self.report_finding(f"[Reflection] Payload reflected at: {test_url}")
                                    print(f"[!!!] Reflection at {test_url}")
                                else:
                                    print(f"[OK] Tested {test_url}")

                    except Exception as e:
                        print(f"[FuzzingAgent] Error testing {test_url}: {e}")

        async def directory_fuzz(self, url):
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            if base_url in self.fuzzed_hosts:
                return

            print(f"[FuzzingAgent] Starting directory fuzz on {base_url}")
            self.fuzzed_hosts.add(base_url)

            common_dirs = ["admin", "login", "dashboard", "config"]
            for dir in common_dirs:
                test_url = f"{base_url}/{dir}"

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(test_url, timeout=10) as resp:
                            if resp.status == 200:
                                await self.report_finding(f"[+] Found interesting path: {test_url} [Status: {resp.status}]")
                                print(f"[+] Found interesting path: {test_url} [Status: {resp.status}]")

                except Exception as e:
                    print(f"[FuzzingAgent] Directory fuzz error on {test_url}: {e}")

        async def report_finding(self, finding):
            msg = Message(to="reporter_agent@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = finding
            await self.send(msg)
            print(f"[FuzzingAgent] Reported finding to ReporterAgent: {finding}")

    async def setup(self):
        print("[FuzzingAgent] Agent launched.")
        self.add_behaviour(self.FuzzingBehaviour())
