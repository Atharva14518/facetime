"use client";

/**
 * Facetime's editorial landing page: an aurora hero, a compact portrait gallery,
 * the proof strip, benefits, four-step accordion, creator examples and CTA.
 */
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { pillClass } from "@/components/ds";
import { IconChevron } from "@/components/ds/icons";
import { useCountUp, useInView } from "@/components/ds/motion";
import { BUILT_ON, MEASUREMENTS, TESTIMONIALS } from "@/lib/site-content";

export function Landing() {
  return (
    <main id="main" className="bg-ink font-sans text-ink">
      <Hero />
      <Stats />
      <HowItWorks />
      <Creators />
      <Quotes />
    </main>
  );
}

// ---------------------------------------------------------------- hero

function Hero() {
  return (
    <section className="relative overflow-hidden bg-[linear-gradient(145deg,#B8F5E6_0%,#D8F2FF_50%,#FFE2EA_100%)]">
      <svg aria-hidden="true" viewBox="0 0 1440 900" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
        <g fill="none" stroke="#FFFFFF" strokeOpacity="0.55" strokeWidth="34" strokeLinecap="round">
          <path d="M760 -40 C 940 120, 1180 160, 1500 120" />
          <path d="M820 120 C 1000 260, 1240 300, 1520 260" strokeOpacity="0.35" />
          <path d="M-60 560 C 200 470, 420 520, 600 640" strokeOpacity="0.3" />
        </g>
      </svg>

      <header className="lk-drop relative mx-auto flex max-w-[1320px] flex-wrap items-center gap-x-7 gap-y-1 px-4 py-4 sm:px-8 sm:py-5">
        <Link href="/" className="font-display text-[18px] font-black tracking-[0.02em] text-ink no-underline sm:text-[20px]">
          FACETIME
        </Link>
        <nav aria-label="Main" className="order-3 flex w-full flex-wrap gap-x-4 text-[13px] font-medium sm:gap-x-7 sm:text-[14px] md:order-none md:w-auto md:flex-1">
          <a href="#how" className="py-3 text-ink no-underline hover:underline">
            How it works
          </a>
          <Link href="/market" className="py-3 text-ink no-underline hover:underline">
            Creators
          </Link>
          <Link href="/status#contracts" className="py-3 text-ink no-underline hover:underline">
            For AI tools
          </Link>
          <Link href="/verify" className="py-3 text-ink no-underline hover:underline">
            Verify
          </Link>
        </nav>
        <div className="ml-auto flex items-center gap-4">
          <Link href="/dashboard" className="hidden py-3 text-[14px] font-medium text-ink no-underline hover:underline sm:inline">
            Log in
          </Link>
          <Link href="/brand/onboard" className={pillClass("outline-dark", "hidden px-5 text-[14px] sm:inline-flex")}>
            License a face
          </Link>
          <Link href="/onboard" className={pillClass("ink", "px-5 text-[14px]")}>
            Become a creator
          </Link>
        </div>
      </header>

      <div className="relative mx-auto grid max-w-[1320px] gap-12 px-4 pb-16 pt-8 sm:px-8 sm:pb-24 sm:pt-16 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
        <div className="lk-drop relative z-10 max-w-[690px]">
          <span className="mb-5 inline-flex rounded-full border border-ink/15 bg-white/65 px-4 py-2 text-[12px] font-bold tracking-[0.13em] text-ink backdrop-blur">
            FACE LICENSING, ON YOUR TERMS
          </span>
          <h1 className="m-0 font-display text-[clamp(52px,7vw,104px)] font-black leading-[0.88] tracking-[-0.045em] text-ink">
            YOUR FACE.
            <br />
            <span className="lk-texture">YOUR RULES.</span>
          </h1>
          <p className="mb-0 mt-7 max-w-[580px] text-[clamp(17px,1.8vw,21px)] leading-relaxed text-[#31405C]">
            Verify once, approve every licence, and get paid when AI uses your likeness. Your identity stays yours.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/onboard" className={pillClass("ink", "min-h-[54px] px-7 text-[15px]")}>Become a creator</Link>
            <a href="#how" className={pillClass("outline-dark", "min-h-[54px] px-7 text-[15px]")}>See how it works</a>
          </div>
          <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-[13px] font-semibold text-[#40506C]">
            <span>18+ verified adults</span><span>Passkey protected</span><span>Revoke any time</span>
          </div>
        </div>

        <div className="lk-rise relative mx-auto min-h-[500px] w-full max-w-[660px] sm:min-h-[620px]">
          <div className="absolute left-[2%] top-[8%] h-[74%] w-[58%] rotate-[-3deg] overflow-hidden rounded-[34px] border-[7px] border-white shadow-[0_28px_70px_rgba(8,18,37,0.22)]">
            <Image src="/landing/facetime-face-coral.png" alt="Fictional adult creator example" fill priority sizes="(min-width:1024px) 400px, 60vw" className="object-cover" />
          </div>
          <div className="absolute right-[2%] top-0 h-[42%] w-[38%] rotate-[5deg] overflow-hidden rounded-[28px] border-[6px] border-white shadow-[0_20px_50px_rgba(8,18,37,0.18)]">
            <Image src="/landing/facetime-face-mint.png" alt="Fictional adult creator example" fill priority sizes="(min-width:1024px) 250px, 38vw" className="object-cover" />
          </div>
          <div className="absolute bottom-[3%] right-[5%] h-[43%] w-[40%] rotate-[3deg] overflow-hidden rounded-[28px] border-[6px] border-white shadow-[0_20px_50px_rgba(8,18,37,0.2)]">
            <Image src="/landing/facetime-face-sky.png" alt="Fictional adult creator example" fill priority sizes="(min-width:1024px) 260px, 40vw" className="object-cover" />
          </div>
          <span className="absolute bottom-[12%] left-0 rounded-full bg-ink px-4 py-2.5 text-[12px] font-bold text-white shadow-lg">✓ VERIFIED HUMAN</span>
          <span className="absolute right-[1%] top-[42%] rounded-full bg-white px-4 py-2.5 text-[12px] font-bold text-ink shadow-lg">PAID PER RENDER</span>
        </div>
      </div>

      <div className="relative border-t border-ink/10 bg-white/40">
      <div className="mx-auto flex max-w-[1180px] flex-wrap items-center justify-center gap-x-[clamp(24px,4.4vw,64px)] gap-y-3 px-4 py-7 text-[clamp(14px,1.4vw,17px)] font-semibold text-[#40506C] sm:px-8">
        <span className="text-[12px] font-bold uppercase tracking-[0.14em] text-[#66738C]">Built on</span>
        {BUILT_ON.map((b) => (
          <span key={b}>{b}</span>
        ))}
      </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- dark benefits block

function Toggle() {
  return (
    <span aria-hidden="true" className="inline-flex h-[42px] w-[96px] items-center gap-1 rounded-full bg-[linear-gradient(90deg,#53E2C2,#D63863)] px-1">
      <span className="h-[34px] w-[34px] rounded-full bg-[#E5FFF8]" />
      <span className="h-[34px] w-[34px] rounded-full bg-[#FFE1E9]" />
    </span>
  );
}

function Stats() {
  const { ref, seen } = useInView<HTMLDivElement>();
  const ms = useCountUp(MEASUREMENTS.registerMs.value, seen);
  const pct = useCountUp(MEASUREMENTS.rendersWithReceipt.value, seen);
  return (
    <section className="on-dark bg-ink text-white">
      <div ref={ref} className="mx-auto flex max-w-[1180px] flex-col gap-10 px-4 py-24 sm:px-8">
        <h2 className={`rv${seen ? " in" : ""} m-0 flex flex-wrap items-center gap-x-4 font-display text-[clamp(28px,4vw,44px)] font-extrabold leading-[1.15] tracking-[-0.01em]`}>
          LICENSE REAL FACES,
          <br />
          WITH
          <span className={`pop${seen ? " in" : ""}`}>
            <Toggle />
          </span>
          CONSENT ATTACHED
        </h2>
        <div className="flex flex-wrap gap-5">
          <article className={`rv${seen ? " in" : ""} relative flex min-h-[340px] min-w-0 flex-[2_1_560px] flex-col gap-4 overflow-hidden rounded-[30px] bg-[linear-gradient(135deg,#D8F2FF_0%,#F0F5FF_58%,#FFFFFF_100%)] p-8 text-ink`} style={{ transitionDelay: ".1s" }}>
            <span aria-hidden="true" className="flex h-[42px] w-[72px] items-center gap-1 rounded-full border-2 border-ink px-1">
              <span className="h-8 w-8 rounded-full bg-ink" />
              <span className="h-8 w-8 rounded-full border-2 border-ink bg-lime" />
            </span>
            <div aria-hidden="true" className="absolute right-10 top-10 hidden h-[210px] w-[260px] sm:block">
              <span className="absolute left-2 top-4 h-[92px] w-[92px] rounded-[28px] bg-lime shadow-[0_16px_30px_rgba(8,18,37,.12)]" />
              <span className="absolute left-[82px] top-[93px] h-1 w-[100px] origin-left rotate-[33deg] rounded bg-violet" />
              <span className="absolute bottom-0 right-1 flex h-[104px] w-[104px] items-center justify-center rounded-full bg-ink font-display text-[32px] font-black text-white shadow-[0_16px_30px_rgba(8,18,37,.16)]">✓</span>
            </div>
            <span className="mt-auto self-start rounded-full bg-violet-deep px-3.5 py-1.5 text-[13px] font-semibold text-white">For brands</span>
            <h3 className="m-0 font-display text-[clamp(20px,2.4vw,26px)] font-extrabold">VERIFIED HUMANS ONLY</h3>
            <p className="m-0 max-w-[460px] text-[15px] leading-relaxed text-[#3E4148]">
              Every creator passed an ID check, a liveness selfie and a face match. Their photos were captured live, so nobody can license a face that
              isn&apos;t theirs.
            </p>
          </article>
          <div className="flex min-w-0 flex-[1_1_300px] flex-col gap-5">
            <article className={`rv${seen ? " in" : ""} flex flex-1 flex-col gap-1.5 rounded-[30px] bg-lime bg-[url(/landing/card-lime.png)] bg-cover bg-center p-7 text-ink`} style={{ transitionDelay: ".25s" }} title={MEASUREMENTS.registerMs.source}>
              <span className="tnum font-display text-[clamp(40px,5vw,52px)] font-black leading-none">{ms} MS</span>
              <span className="font-display text-[17px] font-bold leading-snug">TO REGISTER A CREATOR ON MONAD</span>
              <span className="text-[13px] text-[#3E4148]">Measured on Monad testnet, send to receipt.</span>
            </article>
            <article className={`rv${seen ? " in" : ""} flex flex-1 flex-col gap-1.5 rounded-[30px] bg-ink-line p-7 text-white`} style={{ transitionDelay: ".4s" }} title={MEASUREMENTS.rendersWithReceipt.source}>
              <span className="tnum font-display text-[clamp(40px,5vw,52px)] font-black leading-none text-lime">{pct}%</span>
              <span className="font-display text-[17px] font-bold leading-snug">OF RENDERS CARRY A RECEIPT</span>
              <span className="text-[13px] text-grey-dark">By design: payment and receipt are one transaction.</span>
            </article>
          </div>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- how it works

const STEPS = [
  { title: "PROVE IT'S YOU", body: "An ID check for 18+, a liveness selfie, and three guided photos matched to it. The verification session is deleted once you're attested." },
  { title: "SET YOUR TERMS", body: "Pick uses, regions, a price per render and a cap. Political, adult, minor-involving, impersonating and deceptive uses are banned in the contract." },
  { title: "APPROVE BRANDS", body: "A brand requests a licence and you approve it. Your photos are released to that licence only, unlocked with your passkey (Face ID or Touch ID)." },
  { title: "GET PAID, OR REVOKE", body: "Each render pays you and records a receipt in one Monad transaction. Revoke and the next render is refused." },
];

function HowItWorks() {
  const [open, setOpen] = useState(0);
  const { ref, seen } = useInView<HTMLDivElement>();
  const c = (k: string) => `${k}${seen ? " in" : ""}`;
  return (
    <section id="how" className="scroll-mt-4 overflow-hidden bg-white">
      <div ref={ref} className="mx-auto flex max-w-[1180px] flex-col gap-12 px-4 py-24 sm:px-8">
        <h2 className="m-0 text-center font-display text-[clamp(28px,4vw,44px)] font-extrabold leading-[1.2] tracking-[-0.01em]">
          <span className={`${c("from-l")} inline-block`}>FROM SELFIE</span>{" "}
          <span aria-hidden="true" className={`${c("pop")} inline-flex h-12 w-24 items-center gap-1 rounded-full bg-ink px-[5px] align-middle`}>
            <span className="h-[38px] w-[38px] rounded-full bg-lime" />
            <span className="h-[38px] w-[38px] rounded-full border-2 border-lime" />
          </span>{" "}
          <span className={`${c("from-r")} inline-block`}>TO PAID RENDER</span>
          <br />
          <span className={`${c("rv")} inline-block`}>IN FOUR STEPS</span>
        </h2>
        <div className="flex flex-wrap items-start gap-10">
          <ol className="m-0 flex min-w-0 flex-[1_1_460px] list-none flex-col gap-3.5 p-0">
            {STEPS.map((s, i) => {
              const isOpen = open === i;
              return (
                <li key={s.title} className={`${c("rv")} rounded-[20px] bg-sky-soft px-[22px] py-5`} style={{ transitionDelay: `${0.15 + i * 0.12}s` }}>
                  <h3 className="m-0">
                    <button
                      type="button"
                      aria-expanded={isOpen}
                      aria-controls={`step-${i}`}
                      onClick={() => setOpen(isOpen ? -1 : i)}
                      className="flex min-h-11 w-full cursor-pointer items-center gap-3.5 border-0 bg-transparent p-0 text-left text-ink"
                    >
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink font-sans font-semibold text-white">{i + 1}</span>
                      <span className="flex-1 font-display text-[16px] font-bold">{s.title}</span>
                      <IconChevron size={20} className={`transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`} />
                    </button>
                  </h3>
                  <div id={`step-${i}`} className={`acc-body${isOpen ? " open" : ""}`}>
                    <div className="overflow-hidden">
                      <p className="m-0 mt-3 pl-[50px] text-[15px] leading-relaxed text-[#3E4148]">{s.body}</p>
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
          <div className={`${c("rv")} flex min-w-0 flex-[1_1_440px] flex-col gap-[18px]`} style={{ transitionDelay: ".3s" }}>
            <p className="m-0 text-[16px] leading-relaxed text-[#3E4148]">
              Political, adult and deceptive uses are banned in the contract itself. You choose everything else, and you can pull a licence back in one
              click.
            </p>
            <div className="relative aspect-[5/4] overflow-hidden rounded-[28px] bg-[linear-gradient(145deg,#081225,#17325A)] p-6 text-white sm:p-9">
              <div className="absolute -right-16 -top-14 h-64 w-64 rounded-full bg-lime/20 blur-2xl" />
              <div className="relative flex h-full flex-col rounded-[22px] border border-white/15 bg-white/10 p-5 backdrop-blur">
                <span className="text-[11px] font-bold tracking-[.14em] text-lime">LIVE LICENCE</span>
                <h3 className="mb-1 mt-4 font-display text-[24px] font-extrabold">Studio campaign</h3>
                <p className="m-0 text-[13px] text-white/65">Social · Worldwide · 30 days</p>
                <div className="my-5 h-px bg-white/15" />
                <div className="grid grid-cols-2 gap-3 text-[12px]">
                  <span className="rounded-xl bg-white/10 p-3"><b className="block text-[17px] text-lime">$12</b>per render</span>
                  <span className="rounded-xl bg-white/10 p-3"><b className="block text-[17px] text-lime">250</b>render cap</span>
                </div>
                <div className="mt-auto flex items-center justify-between gap-3 rounded-xl bg-white px-4 py-3 text-ink">
                  <span className="text-[12px] font-bold">Creator approved</span>
                  <span className="rounded-full bg-lime px-3 py-1 text-[11px] font-bold">ACTIVE</span>
                </div>
              </div>
            </div>
            <Link href="/onboard" className={pillClass("ink", "min-h-[54px]")}>
              Get started
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- creators

/**
 * Sample images only, never a real creator's face: each card is labelled Example and invites a creator.
 * Real creators are in the marketplace, with the photo they chose to publish there.
 */
const EXAMPLES = [
  { photo: "/landing/facetime-face-coral.png", tone: "bg-[#FFE1E9]", use: "EDITORIAL" },
  { photo: "/landing/facetime-face-mint.png", tone: "bg-[#B8F5E6]", use: "ADVERTISING" },
  { photo: "/landing/facetime-face-sky.png", tone: "bg-[#DDE1FF]", use: "SOCIAL" },
];

function Creators() {
  const { ref, seen } = useInView<HTMLDivElement>();
  return (
    <section className="relative overflow-hidden bg-sky-soft">
      <div ref={ref} className="relative mx-auto max-w-[1180px] px-4 py-24 sm:px-8">
        <div className={`rv${seen ? " in" : ""} mb-10 flex flex-wrap items-end justify-between gap-5`}>
          <div>
            <span className="text-[12px] font-bold tracking-[.14em] text-[#52627C]">YOUR LIKENESS, YOUR CALL</span>
            <h2 className="mb-0 mt-3 font-display text-[clamp(30px,4vw,48px)] font-extrabold leading-[1.05]">ONE FACE.<br />ENDLESS POSSIBILITY.</h2>
          </div>
          <p className="m-0 max-w-[430px] text-[16px] leading-relaxed text-[#40506C]">Publish one photo, then choose exactly who can use it, where it can appear, and what every render is worth.</p>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {EXAMPLES.map((ex, i) => (
            <Link key={ex.photo} href="/onboard" className={`rv${seen ? " in" : ""} group overflow-hidden rounded-[28px] text-ink no-underline shadow-[0_16px_40px_rgba(8,18,37,.1)] ${ex.tone} ${i === 1 ? "md:translate-y-8" : ""}`} style={{ transitionDelay: `${0.12 + i * 0.14}s` }}>
              <div className="relative aspect-[4/5] overflow-hidden">
                <Image src={ex.photo} alt="Fictional adult creator example" fill sizes="(min-width:768px) 33vw, 92vw" className="object-cover transition-transform duration-500 group-hover:scale-[1.025]" />
                <span className="absolute left-5 top-5 rounded-full bg-white/90 px-3 py-1.5 text-[11px] font-bold tracking-[.1em] backdrop-blur">{ex.use}</span>
              </div>
              <div className="flex items-center justify-between gap-4 p-5">
                <span><b className="block font-display text-[15px]">YOUR FACE HERE</b><span className="text-[12px] text-[#52627C]">You set every term</span></span>
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-ink text-xl text-white">→</span>
              </div>
            </Link>
          ))}
        </div>
        <div className="mt-16 text-center"><Link href="/onboard" className={pillClass("ink", "min-h-[54px] px-8 text-[15px]")}>Add your face</Link></div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- testimonials and CTA

function Quotes() {
  const { ref, seen } = useInView<HTMLDivElement>();
  const c = (k: string) => `${k}${seen ? " in" : ""}`;
  const bgs = [
    ["#0C5965", "#FFFFFF"],
    ["#D8F2FF", "#081225"],
    ["#FFE1E9", "#081225"],
    ["#DDE1FF", "#081225"],
    ["#B8F5E6", "#081225"],
  ];
  return (
    <section className="overflow-hidden bg-white">
      <div ref={ref} className="flex flex-col gap-11 py-24">
        {TESTIMONIALS.length > 0 && (
          <>
            <h2 className="m-0 px-4 text-center font-display text-[clamp(28px,4vw,44px)] font-extrabold leading-[1.2] sm:px-8">
              <span className={`${c("from-l")} inline-block`}>HEAR IT</span>{" "}
              <span aria-hidden="true" className={`${c("pop")} inline-flex h-12 w-24 items-center gap-1 rounded-full bg-lime px-[5px] align-middle`}>
                <span className="h-[38px] w-[38px] rounded-full bg-ink" />
                <span className="h-[38px] w-[38px] rounded-full border-2 border-ink" />
              </span>{" "}
              <span className={`${c("from-r")} inline-block`}>FROM CREATORS</span>
            </h2>
            <div className="lk-marquee overflow-hidden" aria-label="Quotes, scrolling; hover or focus to pause" tabIndex={0}>
              <div className="lk-quotes">
                {[...TESTIMONIALS, ...TESTIMONIALS].map((q, i) => (
                  <blockquote
                    key={i}
                    aria-hidden={i >= TESTIMONIALS.length ? true : undefined}
                    className="m-0 box-border flex min-h-[240px] w-[290px] shrink-0 flex-col gap-[18px] rounded-3xl p-6"
                    style={{ background: bgs[i % bgs.length][0], color: bgs[i % bgs.length][1] }}
                  >
                    <p className="m-0 text-[15px] leading-relaxed">{q.quote}</p>
                    <footer className="mt-auto font-display text-[13px] font-bold">
                      {q.name}
                      <br />
                      <span className="font-sans font-normal opacity-80">{q.role}</span>
                    </footer>
                  </blockquote>
                ))}
              </div>
            </div>
          </>
        )}
        <div className="px-4 sm:px-8">
          <div className={`${c("rv")} relative mx-auto flex max-w-[1116px] flex-wrap items-center justify-between gap-5 overflow-hidden rounded-[24px] bg-lime bg-[url(/landing/card-lime.png)] bg-cover bg-center px-[30px] py-[26px]`}>
            <h2 className="m-0 font-display text-[clamp(18px,2.2vw,24px)] font-extrabold leading-[1.25]">
              LICENSE YOUR FACE TO AI.
              <br />
              YOUR TERMS, PAID PER IMAGE.
            </h2>
            <span className="flex flex-wrap items-center gap-3">
              <span className="hidden rounded-full bg-white/70 px-4 py-2 text-[12px] font-bold text-ink sm:inline-flex">18+ · VERIFIED · IN CONTROL</span>
              <Link href="/brand/onboard" className={pillClass("outline-dark", "px-6 text-[14px]")}>
                License a face
              </Link>
              <Link href="/onboard" className={pillClass("ink", "px-6 text-[14px]")}>
                Get started
              </Link>
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
