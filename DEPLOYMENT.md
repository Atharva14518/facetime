# Deploying Likeness

The deployable application is the Next.js project in `web/`. This repository supports two hosting
targets:

- **Vercel:** serverless Next.js with a private Vercel Blob store.
- **Render:** one Docker web service with a persistent disk mounted at `/data`.

Treat them as separate environments (for example, Vercel production and Render staging). They do not
share data: Vercel writes to Blob and Render writes to its disk. Passkeys are also bound to an RP ID,
so unrelated `vercel.app` and `onrender.com` hosts must use different `NEXT_PUBLIC_RP_ID` values.

## Before deploying

1. Keep every secret out of Git. `.env`, `.env.local`, `.secrets/`, `*.pem`, `*.key`, and `*.ses` are
   ignored. Use each provider's encrypted environment-variable UI.
2. Start with [`web/.env.example`](web/.env.example). The app can boot with integrations disabled,
   and `/status` explains what each missing integration affects.
3. For a fully functional deployment, collect these values:

   | Feature | Environment variables |
   | --- | --- |
   | Public URL and passkeys | `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_RP_ID` |
   | Dynamic sign-in/wallets | `NEXT_PUBLIC_DYNAMIC_ENV_ID`, `DYNAMIC_API_KEY` |
   | Dynamic delegated access | `DYNAMIC_WEBHOOK_SECRET`, `DYNAMIC_DELEGATION_PRIVATE_KEY_PEM`, optionally `DYNAMIC_AGENT_JSON` |
   | Creator verification | `DIDIT_API_KEY`, `DIDIT_WORKFLOW_ID_FREE` (or `DIDIT_WORKFLOW_ID_FULL`) |
   | Attestation and gas | `ATTESTER_PRIVATE_KEY`, `RENDER_AGENT_PRIVATE_KEY`, `DRIP_PRIVATE_KEY` |
   | Image generation | `GEMINI_API_KEY` |
   | C2PA manifests | `C2PA_CERT_PEM`, `C2PA_KEY_PEM` |
   | Optional integrations | `ENVIO_GRAPHQL_URL`, `RESEND_API_KEY`, `MAIL_FROM` |

   Multiline PEM values can be pasted as real multiline values or with `\n` escapes. Never use the
   `*_KEY_FILE` variables on hosted platforms unless you deliberately created provider secret files;
   use the direct values listed above instead.

## Deploy to Render

The root [`render.yaml`](render.yaml) builds [`web/Dockerfile`](web/Dockerfile), checks
`/api/status`, and provisions a 2 GB RAM service plus a 5 GB persistent disk. This uses **billable
Render resources** because persistent disks are unavailable on free web services.

1. In Render, choose **New > Blueprint** and connect `Atharva14518/facetime`.
2. Select branch `main` and the root `render.yaml`.
3. In the initial Blueprint form, provide:
   - `NEXT_PUBLIC_APP_URL=https://facetime-likeness.onrender.com`
   - `NEXT_PUBLIC_RP_ID=facetime-likeness.onrender.com`
   - `NEXT_PUBLIC_DYNAMIC_ENV_ID=<your Dynamic environment ID>`
4. Review the paid service and disk, then apply the Blueprint.
5. If Render assigns a different hostname, change `NEXT_PUBLIC_APP_URL` and
   `NEXT_PUBLIC_RP_ID` to the exact assigned URL/hostname. Choose **Save, rebuild, and deploy** because
   `NEXT_PUBLIC_*` values are compiled during the Docker build.
6. Under **Environment**, add the server-only secrets you collected above. Do not put them in
   `render.yaml`. Choose **Save, rebuild, and deploy**.
7. Add the final Render origin to Dynamic's allowed origins and configure the Didit redirect/webhook
   URLs for the same origin.
8. Verify:
   - `https://<render-host>/api/status` returns JSON with HTTP 200.
   - `https://<render-host>/status` shows the expected integrations as configured.

The container downloads the pinned face models to `/data/models` on first boot. The disk preserves the
models, ciphertext, records, rendered files, and history cache across redeploys.

## Deploy to Vercel

1. In Vercel, choose **Add New > Project**, import `Atharva14518/facetime`, and set **Root Directory**
   to `web`.
2. Keep the detected **Next.js** framework. `web/vercel.json` supplies the pinned pnpm install and build
   commands.
3. Create a **private Vercel Blob store** and connect it to this project. Vercel adds
   `BLOB_READ_WRITE_TOKEN`; also set `STORE_DRIVER=blob`.
4. Add the variables from the table above to the **Production** environment. At minimum set:
   - `NEXT_PUBLIC_APP_URL=https://<your-production-host>`
   - `NEXT_PUBLIC_RP_ID=<your-production-host-without-https>`
   - `NEXT_PUBLIC_DYNAMIC_ENV_ID=<your Dynamic environment ID>`
   - `NEXT_PUBLIC_MONAD_RPC_URL=https://testnet-rpc.monad.xyz`
   - `MONAD_RPC_URL=https://testnet-rpc.monad.xyz`
   - `VERIFICATION_LEVEL=free`
5. Deploy. If you add or change the domain afterward, update both URL variables and redeploy without
   the build cache. Add that final origin to Dynamic and Didit.
6. Verify `/api/status` and `/status` as described above.

### Optional Vercel CLI setup

If `web/.env.local` and the local `.secrets/` directory already contain the intended production
values, the guarded helper can upload them without printing them:

```sh
cd web
npx vercel login
npx vercel link
sh scripts/vercel-env.sh https://your-production-domain.example
npx vercel --prod --force
```

The helper displays the linked Vercel project and requires its exact name before writing anything.

## Post-deploy checklist

- `/api/status` is healthy and `/status` reports the intended integrations.
- Dynamic allows the exact production origin.
- The RP ID is the stable production hostname or its parent custom domain; changing it later makes
  existing passkeys unusable on the new RP ID.
- Didit workflows and callbacks use the same public URL.
- The render-agent address is registered in `LicenseEscrow` before enabling paid renders.
- The drip and render-agent wallets contain only the minimum testnet funds needed.
- Render and Vercel test data are kept separate unless the application is migrated to one shared
  external datastore.
