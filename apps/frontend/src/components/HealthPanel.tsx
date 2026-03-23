export function HealthPanel() {
  const services = [
    'api-gateway',
    'market-data-service',
    'quant-engine',
    'ml-service',
    'worker-orchestrator',
  ]

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl shadow-cyan-950/20">
      <h2 className="text-xl font-medium">Phase 1 service shell</h2>
      <p className="mt-2 text-sm text-slate-400">
        Each service exposes a minimal FastAPI health endpoint and is independently containerized.
      </p>
      <ul className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {services.map((service) => (
          <li key={service} className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-200">
            {service}
          </li>
        ))}
      </ul>
    </section>
  )
}
