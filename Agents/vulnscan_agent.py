from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import aiohttp
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class VulnScanAgent(Agent):
    class ScanBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=60)  # Wait for a message for 60s
            if msg:
                print("[VulnScanAgent] Received URLs to scan.")
                urls = msg.body.split("\n")
                for url in urls:
                    await self.test_xss(url)
            else:
                print("[VulnScanAgent] No message received. Retrying...")

        async def test_xss(self, url):
            payload = "<script>alert(1)</script>"

            parsed = urlparse(url)
            qs = parse_qs(parsed.query)

            # Only test if the URL has query parameters
            if not qs:
                print(f"[VulnScanAgent] No parameters to inject in {url}")
                return

            # Inject payload into each parameter
            new_params = {key: payload for key in qs.keys()}
            new_query = urlencode(new_params, doseq=True)
            new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

            print(f"[VulnScanAgent] Testing {new_url}")

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(new_url, timeout=10) as response:
                        body = await response.text()
                        if payload in body:
                            print(f"[!!!] Potential XSS found at: {new_url}")

                            # 📨 SEND finding to ReporterAgent
                            report_msg = Message(to="reporter_agent@localhost")
                            report_msg.set_metadata("performative", "inform")
                            report_msg.body = f"[XSS] Vulnerability detected at: {new_url}"
                            await self.send(report_msg)
                            print("[VulnScanAgent] Reported finding to ReporterAgent.")

                        else:
                            print(f"[OK] No XSS found at: {new_url}")

            except Exception as e:
                print(f"[VulnScanAgent] Failed to test {new_url}: {e}")

    async def setup(self):
        print("[VulnScanAgent] Agent launched.")
        self.add_behaviour(self.ScanBehaviour())
