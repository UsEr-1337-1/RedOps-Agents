import asyncio

from Agents.recon_agent import ReconAgent
from Agents.vulnscan_agent import VulnScanAgent
from Agents.fuzzing_agent import FuzzingAgent
from Agents.auth_agent import AuthAgent
from Agents.reporter_agent import ReporterAgent

async def main():
    recon_agent = ReconAgent("recon_agent@localhost", "pass_recon")
    vulnscan_agent = VulnScanAgent("vulnscan_agent@localhost", "pass_vuln")
    fuzzing_agent = FuzzingAgent("fuzzing_agent@localhost", "pass_fuzz")
    auth_agent = AuthAgent("auth_agent@localhost", "pass_auth")
    reporter_agent = ReporterAgent("reporter_agent@localhost", "pass_report")

    await recon_agent.start(auto_register=True)
    await vulnscan_agent.start(auto_register=True)
    await fuzzing_agent.start(auto_register=True)
    await auth_agent.start(auto_register=True)
    await reporter_agent.start(auto_register=True)

    print("[System] All agents are running...")
    await asyncio.sleep(3600)  # Keep agents alive for 1 hour

if __name__ == "__main__":
    asyncio.run(main())
