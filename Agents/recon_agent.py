from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from spade.message import Message

class ReconAgent(Agent):
    class ReconBehaviour(OneShotBehaviour):
        async def run(self):
            print("[ReconAgent] Starting reconnaissance...")

            base_url = "http://testphp.vulnweb.com/"
            visited = set()
            to_visit = [base_url]

            while to_visit:
                url = to_visit.pop()
                if url in visited:
                    continue
                visited.add(url)

                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, "html.parser")

                    for link in soup.find_all("a"):
                        href = link.get("href")
                        if href:
                            full_url = urljoin(url, href)
                            if base_url in full_url and full_url not in visited:
                                to_visit.append(full_url)

                except Exception as e:
                    print(f"[ReconAgent] Failed to crawl {url}: {e}")

            print("\n[ReconAgent] Discovered URLs:")
            for u in visited:
                print(f" - {u}")



            # 🛑 WAIT before sending
            import asyncio
            await asyncio.sleep(5)

            urls_body = "\n".join(visited)  # Or `found_urls` depending on your naming

            # Message to VulnScanAgent
            msg_vuln = Message(to="vulnscan_agent@localhost")
            msg_vuln.set_metadata("performative", "inform")
            msg_vuln.body = urls_body
            await self.send(msg_vuln)

            # ✅ Message to FuzzingAgent
            msg_fuzz = Message(to="fuzzing_agent@localhost")
            msg_fuzz.set_metadata("performative", "inform")
            msg_fuzz.body = urls_body
            await self.send(msg_fuzz)

            # 🔐 Message to AuthAgent
            msg_auth = Message(to="auth_agent@localhost")
            msg_auth.set_metadata("performative", "inform")
            msg_auth.body = urls_body
            await self.send(msg_auth)

            print("[ReconAgent] Sent discovered URLs to VulnScanAgent and FuzzingAgent and AuthAgent")

    async def setup(self):
        print("[ReconAgent] Agent launched.")
        self.add_behaviour(self.ReconBehaviour())
