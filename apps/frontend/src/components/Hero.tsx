import type { Company } from "../data/dashboardTypes";

type HeroProps = {
	company: Company;
};

export function Hero({ company }: HeroProps) {
	return (
		<section className="hero" id="overview" aria-labelledby="hero-title">
			<div>
				<p className="eyebrow">Financial intelligence dashboard</p>
				<h1 id="hero-title">FinAgentOps</h1>
				<p className="hero__copy">
					A portfolio-ready shell for tracking company KPIs, data pipeline
					health, risk signals, and future AI analyst summaries.
				</p>
			</div>
			<div className="hero__company" aria-label="Selected company summary">
				<span>{company.exchange}</span>
				<strong>{company.ticker}</strong>
				<p>{company.name}</p>
			</div>
		</section>
	);
}
