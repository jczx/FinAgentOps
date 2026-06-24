import type { Kpi } from "../data/dashboardTypes";

type KpiCardsProps = {
	kpis: Kpi[];
};

const trendLabels: Record<Kpi["trend"], string> = {
	up: "Improving",
	down: "Declining",
	flat: "Stable",
};

export function KpiCards({ kpis }: KpiCardsProps) {
	return (
		<section className="kpi-section" aria-labelledby="kpi-heading">
			<div className="section-heading">
				<p className="eyebrow">Key metrics</p>
				<h2 id="kpi-heading">KPI snapshot</h2>
			</div>
			<div className="kpi-grid">
				{kpis.length === 0 ? (
					<article className="kpi-card kpi-card--empty">
						<h3>No metrics available</h3>
						<p>Run SEC ingestion for this company to populate yearly metrics.</p>
					</article>
				) : (
					kpis.map((kpi) => (
						<article className="kpi-card" key={kpi.label}>
							<div className="kpi-card__topline">
								<h3>{kpi.label}</h3>
								<span className={`trend trend--${kpi.trend}`}>
									{trendLabels[kpi.trend]}
								</span>
							</div>
							<strong>{kpi.value}</strong>
							<p>{kpi.description}</p>
						</article>
					))
				)}
			</div>
		</section>
	);
}
