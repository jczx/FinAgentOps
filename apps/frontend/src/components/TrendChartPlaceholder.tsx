import type { TrendPoint } from "../data/dashboardMock";

type TrendChartPlaceholderProps = {
	data: TrendPoint[];
};

export function TrendChartPlaceholder({ data }: TrendChartPlaceholderProps) {
	return (
		<section className="panel chart-panel" aria-labelledby="trend-heading">
			<div className="section-heading">
				<p className="eyebrow">Mock trend</p>
				<h2 id="trend-heading">Financial trend placeholder</h2>
			</div>
			<div className="chart" role="img" aria-label="Mock upward financial trend chart">
				{data.map((point) => (
					<div className="chart__bar-group" key={point.label}>
						<div
							className="chart__bar"
							style={{ height: `${point.value}%` }}
							aria-hidden="true"
						/>
						<span>{point.label}</span>
					</div>
				))}
			</div>
		</section>
	);
}
