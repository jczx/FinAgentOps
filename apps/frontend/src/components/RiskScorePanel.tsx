import type { RiskProfile } from "../data/dashboardTypes";

type RiskScorePanelProps = {
	risk: RiskProfile;
};

export function RiskScorePanel({ risk }: RiskScorePanelProps) {
	return (
		<section className="panel risk-panel" aria-labelledby="risk-heading">
			<p className="eyebrow">Model signal</p>
			<h2 id="risk-heading">Risk score</h2>
			<div className="risk-panel__score">{risk.score}</div>
			<p>{risk.summary}</p>
			<ul>
				{risk.factors.map((factor) => (
					<li key={factor}>{factor}</li>
				))}
			</ul>
		</section>
	);
}
