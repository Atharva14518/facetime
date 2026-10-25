/**
 * Local development launcher.
 *
 * Starts an Anvil fork of Monad testnet, rotates the forked contracts to local-only signing keys,
 * funds the gas-drip account on the fork, and then starts Next.js against that same RPC. Nothing is
 * written to the public testnet.
 */
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { parseEther, type Hex } from "viem";
import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";

if (existsSync(".env.local")) process.loadEnvFile(".env.local");

const root = path.resolve("..");
const secrets = path.join(root, ".secrets");
const bundledAnvil = path.join(root, ".tools", "foundry", "anvil");
process.env.ANVIL_BIN ||= existsSync(bundledAnvil) ? bundledAnvil : path.join(homedir(), ".foundry", "bin", "anvil");

function localKey(name: string): Hex {
  const file = path.join(secrets, name);
  mkdirSync(secrets, { recursive: true, mode: 0o700 });
  if (!existsSync(file)) writeFileSync(file, `${generatePrivateKey()}\n`, { mode: 0o600 });
  const key = readFileSync(file, "utf8").trim();
  if (!/^0x[0-9a-fA-F]{64}$/.test(key)) throw new Error(`${file} is not a valid private key`);
  return key as Hex;
}

async function main() {
  if (!existsSync(process.env.ANVIL_BIN!)) {
    throw new Error(`Anvil is missing at ${process.env.ANVIL_BIN}; install Foundry 1.8.3 or set ANVIL_BIN`);
  }

  // ANVIL_BIN must be set before this module is loaded because it resolves the executable once.
  const { startFork, takeOverRoles } = await import("@/lib/dev/fork");
  const port = Number(process.env.DEV_FORK_PORT ?? 8545);
  const fork = await startFork(port);
  const stateDir = path.resolve(".data", "dev-fork");
  const stateFile = path.join(stateDir, "state.hex");
  mkdirSync(stateDir, { recursive: true });
  if (existsSync(stateFile)) {
    const state = readFileSync(stateFile, "utf8").trim();
    if (/^0x[0-9a-fA-F]+$/.test(state)) await fork.test.loadState({ state: state as Hex });
  }

  const attesterKey = localKey("attester.key");
  const dripKey = localKey("drip.key");
  const agentKey = localKey("render-agent.key");
  const attester = privateKeyToAccount(attesterKey).address;
  const drip = privateKeyToAccount(dripKey).address;
  const agent = privateKeyToAccount(agentKey).address;

  await takeOverRoles(fork, { attester, agent });
  await fork.test.setBalance({ address: drip, value: parseEther("1000") });

  const env = {
    ...process.env,
    MONAD_RPC_URL: fork.url,
    NEXT_PUBLIC_MONAD_RPC_URL: fork.url,
    INDEX_START_BLOCK: String(fork.forkBlock),
    ATTESTER_KEY_FILE: path.join(secrets, "attester.key"),
    DRIP_KEY_FILE: path.join(secrets, "drip.key"),
    RENDER_AGENT_KEY_FILE: path.join(secrets, "render-agent.key"),
  };

  console.log(`Local Monad fork ready at ${fork.url}`);
  console.log(`Local attester: ${attester}`);
  console.log(`Funded local drip: ${drip}`);

  const next = spawn(path.join("node_modules", ".bin", "next"), ["dev", "--hostname", "0.0.0.0"], {
    cwd: process.cwd(),
    env,
    stdio: "inherit",
  });

  let stopping = false;
  const save = async () => writeFileSync(stateFile, `${await fork.test.dumpState()}\n`, { mode: 0o600 });
  const checkpoint = setInterval(() => void save().catch((error) => console.error("Could not checkpoint local fork:", error)), 5_000);
  const stop = async (signal?: NodeJS.Signals) => {
    if (stopping) return;
    stopping = true;
    clearInterval(checkpoint);
    await save().catch((error) => console.error("Could not save local fork:", error));
    if (signal) next.kill(signal);
    fork.stop();
  };
  process.once("SIGINT", () => void stop("SIGINT"));
  process.once("SIGTERM", () => void stop("SIGTERM"));
  next.once("exit", async (code) => {
    await stop();
    process.exitCode = code ?? 1;
  });
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
