import { HealthPanel } from '../components/HealthPanel'

export function App() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-50">
      <section className="mx-auto max-w-5xl space-y-6">
        <header>
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">Phase 1 Bootstrap</p>
          <h1 className="text-4xl font-semibold">Quantitative Derivatives Terminal</h1>
          <p className="mt-3 max-w-3xl text-slate-300">
            React, TypeScript, Tailwind, and Plotly are wired for the terminal shell.
            Runtime data flows, quant pricing, and ML inference are added in later phases.
          </p>
        </header>
        <HealthPanel />
      </section>
    </main>
  )
}
